from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


class ConfigurableRetriever:

    def __init__(
        self,
        top_k=3,
        vector_weight=0.7,
        graph_weight=0.3
    ):

        self.top_k = top_k
        self.vector_weight = vector_weight
        self.graph_weight = graph_weight

        # Sample documents
        self.documents = [
            "Artificial Intelligence is transforming healthcare.",
            "Google developed Transformer architecture.",
            "Neo4j is a graph database.",
            "FAISS enables semantic vector retrieval.",
            "Machine learning powers recommendation systems."
        ]

        # Embedding model
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        # Generate embeddings
        embeddings = self.model.encode(
            self.documents
        )

        embedding_matrix = np.array(
            embeddings
        ).astype("float32")

        # Create FAISS index
        dimension = embedding_matrix.shape[1]

        self.index = faiss.IndexFlatL2(
            dimension
        )

        self.index.add(embedding_matrix)

    def search(self, query):

        print("\nRetrieval Configuration")
        print("-" * 40)

        print(f"Top K Results     : {self.top_k}")
        print(f"Vector Weight     : {self.vector_weight}")
        print(f"Graph Weight      : {self.graph_weight}")

        # Vector Search
        query_embedding = self.model.encode(
            [query]
        ).astype("float32")

        distances, indices = self.index.search(
            query_embedding,
            self.top_k
        )

        print("\nSearch Results")
        print("-" * 40)

        for rank, idx in enumerate(indices[0]):

            print(f"{rank+1}. {self.documents[idx]}")

            print(
                f"Distance Score: "
                f"{distances[0][rank]}"
            )

            print("-" * 40)


if __name__ == "__main__":

    retriever = ConfigurableRetriever(
        top_k=2,
        vector_weight=0.8,
        graph_weight=0.2
    )

    retriever.search(
        "AI applications in healthcare"
    )