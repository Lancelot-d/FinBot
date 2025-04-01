try: 
    from .dao import DAO
except ImportError:
    from dao import DAO
    
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer


def get_top_k_reddit_posts(user_input: str, k: int = 5) -> list[str]:
    """
    Retrieve the top k Reddit posts from the FAISS index based on user input.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Load FAISS index
    index = faiss.read_index("reddit_faiss.index")
    
    # Convert user input to a vector (this requires a text embedding model)
    user_input_vector = embed_text(user_input, model)  # Replace with your embedding function
    user_input_vector = np.array([user_input_vector], dtype="float32")
    
    # Search for the top-k similar vectors
    distances, indices = index.search(user_input_vector, k)
    
    # Retrieve the corresponding Reddit posts
    posts = DAO.get_instance().get_reddit_posts()
    top_k_posts = [posts[i][1] for i in indices[0] if i < len(posts)]
    
    return top_k_posts

def batch_insert():
    """
    Insert documents into the FAISS index in batches.
    """
    model = SentenceTransformer('all-MiniLM-L6-v2')
    posts = DAO.get_instance(force_refresh=True).get_reddit_posts()
    ids = [id[0] for id in posts if id[0] is not None and id[1] is not None]
    documents = [content[1] for content in posts if content[0] is not None and content[1] is not None]
    
    # Convert documents to embeddings 
    embeddings = [embed_text(doc, model) for doc in documents]  
    embeddings = np.array(embeddings, dtype="float32")
    
    # Create a FAISS index
    dimension = embeddings.shape[1] 
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(embeddings)
    
    # Save the index to a file
    faiss.write_index(index, "reddit_faiss.index")

def embed_text(text: str, model) -> np.ndarray:
    """
    Convert text into an embedding vector using SentenceTransformers.
    """
    return model.encode(text, convert_to_numpy=True)

def main():
    """
    Main function to execute the script.
    """
    print("Starting batch insertion of Reddit posts into FAISS index...")
    batch_insert()
    print("Batch insertion completed.")

if __name__ == "__main__":
    main()