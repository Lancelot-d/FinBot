
from dao import DAO
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
import time

MODEL_NAME_EMBEDDING = "paraphrase-MiniLM-L3-v2"


def get_top_k_reddit_posts(user_input: str, k: int = 5) -> list[str]:
    """
    Retrieve the top k Reddit posts from the FAISS index based on user input.
    """
    model = SentenceTransformer(MODEL_NAME_EMBEDDING)
    # Load FAISS index
    index = faiss.read_index("reddit_faiss.index")

    # Convert user input to a vector (this requires a text embedding model)
    user_input_vector = embed_text(
        user_input, model
    )  # Replace with your embedding function
    user_input_vector = np.array([user_input_vector], dtype="float32")

    # Search for the top-k similar vectors
    distances, indices = index.search(user_input_vector, k)

    # Retrieve the corresponding Reddit posts
    posts = DAO.get_instance().get_reddit_posts()
    top_k_posts = [posts[i][1] for i in indices[0] if i < len(posts)]

    return top_k_posts

def embed_text(text: str, model) -> np.ndarray:
    """
    Convert text into an embedding vector using SentenceTransformers.
    """
    return model.encode(text, convert_to_numpy=True, show_progress_bar=False)

def batch_insert():
    """
    Insert documents into the FAISS index in batches.
    """
    start = time.perf_counter()
    model = SentenceTransformer(MODEL_NAME_EMBEDDING)
    posts = DAO.get_instance(force_refresh=True).get_reddit_posts()
    documents = [
        content[1]
        for content in posts
        if content[0] is not None and content[1] is not None
    ]
    end = time.perf_counter()
    print(f"Time taken to fetch posts: {end - start:.2f} seconds")

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as executor:
        embeddings = list(executor.map(lambda doc: embed_text(doc, model), documents))

    embeddings = np.array(embeddings, dtype="float32")
    end = time.perf_counter()
    print(f"Time taken to embed posts: {end - start:.2f} seconds")

    start = time.perf_counter()
    # Create a FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    # Add embeddings to the index
    index.add(embeddings)

    # Save the index to a file
    faiss.write_index(index, "reddit_faiss.index")
    end = time.perf_counter()
    print(f"Time taken to create and save FAISS index: {end - start:.2f} seconds")