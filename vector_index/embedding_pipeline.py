from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

documents = [
    "Artificial Intelligence is transforming healthcare.",
    "Google developed the Transformer architecture.",
    "Neo4j is a graph database.",
    "FAISS enables semantic vector search."
]

def generate_embeddings(docs):
    embeddings = model.encode(docs)

    print("\n Embeddings Generated Successfully!\n")

    for i, emb in enumerate(embeddings):
        print(f"Document {i+1}:")
        print(docs[i])
        print(f"Embedding Shape: {np.array(emb).shape}")
        print("-" * 50)

    return embeddings

if __name__ == "__main__":
    generate_embeddings(documents)