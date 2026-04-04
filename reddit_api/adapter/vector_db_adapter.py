"""Vector database adapter for similarity search on Reddit posts."""

import os
import sys
from functools import lru_cache
from typing import Any
import numpy as np

try:
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import chromadb
from sentence_transformers import SentenceTransformer
from dao import DAO
from logger_config import logger

MODEL_NAME_EMBEDDING = "paraphrase-MiniLM-L3-v2"
CHROMA_COLLECTION_NAME = "reddit_posts"
CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
SYNC_BATCH_SIZE = int(os.getenv("VECTOR_SYNC_BATCH_SIZE", "2048"))


def embed_text(text: str, model: SentenceTransformer) -> np.ndarray:
    """
    Convert text into an embedding vector using SentenceTransformers.
    """
    return model.encode(text, convert_to_numpy=True, show_progress_bar=False)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Get a cached embedding model instance to avoid repeated loads."""
    logger.info("Loading embedding model=%s", MODEL_NAME_EMBEDDING)
    return SentenceTransformer(MODEL_NAME_EMBEDDING)


def get_reddit_posts() -> list[tuple[str, str]]:
    """
    Retrieve Reddit posts from the DAO.
    Returns a list of tuples (post_id, post_content).
    """
    logger.info("Loading reddit posts from DAO for vector indexing")
    reddit_posts = DAO.get_instance(force_refresh=True).get_reddit_posts() or []
    return [
        (post.id, post.content_str)
        for post in reddit_posts
        if post.id is not None and post.content_str is not None
    ]


def get_collection() -> Any:
    """
    Get or create the Chroma collection that stores Reddit post embeddings.
    """
    logger.info(
        "Connecting to Chroma collection=%s host=%s port=%s",
        CHROMA_COLLECTION_NAME,
        CHROMA_HOST,
        CHROMA_PORT,
    )
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)


def get_top_k_reddit_posts(user_input: str, k: int = 5) -> list[str]:
    """
    Retrieve the top k Reddit posts from ChromaDB based on user input.
    """
    if k <= 0:
        return []

    model = get_embedding_model()
    collection = get_collection()
    collection_count = collection.count()
    if collection_count == 0:
        logger.info("Chroma collection is empty, no context posts available")
        return []

    n_results = min(k, collection_count)

    user_input_vector = embed_text(user_input, model).astype("float32")
    result = collection.query(
        query_embeddings=[user_input_vector.tolist()],
        n_results=n_results,
    )
    logger.info("Retrieved top %d reddit posts from Chroma", n_results)

    return result.get("documents", [[]])[0]


def _chunked(items: list[tuple[str, str]], batch_size: int) -> list[list[tuple[str, str]]]:
    """Split items into fixed-size batches."""
    return [items[i : i + batch_size] for i in range(0, len(items), batch_size)]


def _chunked_ids(ids: list[str], batch_size: int) -> list[list[str]]:
    """Split IDs into fixed-size batches."""
    return [ids[i : i + batch_size] for i in range(0, len(ids), batch_size)]


def _get_existing_ids(collection: Any, ids: list[str]) -> set[str]:
    """Get IDs that already exist in Chroma for a given batch."""
    if not ids:
        return set()

    existing = collection.get(ids=ids, include=["metadatas"])
    return set(existing.get("ids", []))


def sync_new_posts(batch_size: int = SYNC_BATCH_SIZE) -> int:
    """
    Incrementally insert only new posts into ChromaDB.

    Returns:
        Number of newly indexed posts.
    """
    logger.info("Starting incremental vector sync to Chroma")
    dao = DAO.get_instance(force_refresh=True)
    all_post_ids = dao.get_reddit_post_ids()

    if not all_post_ids:
        logger.warning("No posts available for vector indexing")
        return 0

    model = get_embedding_model()
    collection = get_collection()

    inserted_count = 0
    for batch_ids in _chunked_ids(all_post_ids, max(batch_size, 1)):
        existing_ids = _get_existing_ids(collection, batch_ids)
        new_ids = [post_id for post_id in batch_ids if post_id not in existing_ids]

        if not new_ids:
            continue

        new_posts = dao.get_reddit_posts_by_ids(new_ids)
        if not new_posts:
            continue

        ids = [post_id for post_id, _ in new_posts]
        documents = [content for _, content in new_posts]
        embeddings = (
            model.encode(documents, convert_to_numpy=True, show_progress_bar=False)
            .astype("float32")
            .tolist()
        )
        collection.upsert(ids=ids, documents=documents, embeddings=embeddings)
        inserted_count += len(ids)

    logger.info(
        "Incremental vector sync completed: inserted=%d total_seen=%d",
        inserted_count,
        len(all_post_ids),
    )
    return inserted_count
