from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# Sample documents
documents = [
    "Artificial Intelligence is transforming healthcare.",
    "Google developed the Transformer architecture.",
    "Neo4j is a graph database.",
    "FAISS enables semantic vector search.",
    "Machine learning powers recommendation systems."
]

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings
embeddings = model.encode(documents)

# Convert to float32 for FAISS
embedding_matrix = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = embedding_matrix.shape[1]

index = faiss.IndexFlatL2(dimension)

# Add embeddings to index
index.add(embedding_matrix)

print(f"\n FAISS index created with {index.ntotal} documents")

# ----------------------------
# Semantic Search
# ----------------------------

query = "AI applications in medicine"

query_embedding = model.encode([query]).astype("float32")

# Search top 3 similar docs
k = 3

distances, indices = index.search(query_embedding, k)

print(f"\n Query: {query}\n")

print("Top Matches:\n")

for rank, idx in enumerate(indices[0]):
    print(f"{rank+1}. {documents[idx]}")
    print(f"Distance Score: {distances[0][rank]}")
    print("-" * 50)