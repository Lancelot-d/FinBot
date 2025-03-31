#https://discuss.streamlit.io/t/issues-with-chroma-and-sqlite/47950/4
try:
    __import__('pysqlite3')
    import sys
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except:
    pass

import chromadb
from .dao import DAO
import os 

COLLECTION_NAME = "reddit_embeddings"

def get_top_k_reddit_posts(user_input : str, k: int = 5) -> list[str]:
    """
    Retrieve the top k Reddit posts from the database.
    """
    collection = get_chroma_collection(collection_name=COLLECTION_NAME)
    if collection is None:
        collection = create_chroma_collection(collection_name=COLLECTION_NAME)
    
    return collection.query(
        query_texts=[user_input],
        n_results=k,
    )["documents"][0]
    
def batch_insert():
    """
    Insert documents into the ChromaDB collection in batches.
    """
    posts = DAO.get_instance(force_refresh=True).get_reddit_posts()
    ids = [id[0] for id in posts if id[0] is not None and id[1] is not None]
    documents = [content[1] for content in posts if content[0] is not None and content[1] is not None]
    
    collection = get_chroma_collection(collection_name=COLLECTION_NAME)
    if collection is None:
        collection = create_chroma_collection(collection_name=COLLECTION_NAME)
    
    batch_size = 1000
    for i in range(0, len(documents), batch_size):
        batch_documents = documents[i : i + batch_size]
        batch_ids = ids[i : i + batch_size]
        add_posts_to_chroma(documents=batch_documents, ids=batch_ids, collection=collection)

def get_chroma_client():
    """
    Retrieve the ChromaDB client instance.
    """
    try:
        return chromadb.PersistentClient()
    except Exception as e:
        print("Error connecting to ChromaDB:", e)
  
  
def get_chroma_collection(collection_name: str):
    """
    Retrieve a collection from ChromaDB.
    """
    try:
        collection = get_chroma_client().get_collection(name=collection_name)
        return collection
    except Exception as e:
        print(f"Error retrieving collection {collection_name}: {e}")
        return None
    
def create_chroma_collection(collection_name: str):
    """
    Create a collection in ChromaDB if it doesn't already exist.
    """
    try:
        collection = get_chroma_client().create_collection(name=collection_name)
        return collection
    except Exception as e:
        print(f"Error creating collection {collection_name}: {e}")
        return None
    
def add_posts_to_chroma(documents: list[str], ids: list[str], collection) -> bool:
    try:
        collection.add(
            documents=documents,
            ids=ids
        )
        return True
    except Exception as e:
        print(f"Error adding posts to ChromaDB: {e}")
        

def main():
    """
    Main function to execute the script.
    """
    print("Starting batch insertion of Reddit posts into ChromaDB...")
    batch_insert()
    print("Batch insertion completed.")
    
if __name__ == "__main__":
    main()