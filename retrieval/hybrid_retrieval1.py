from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


class HybridRetriever:

    def __init__(self):

        # Sample documents
        self.documents = [
            "Artificial Intelligence is transforming healthcare.",
            "Google developed the Transformer architecture.",
            "Neo4j is a graph database.",
            "FAISS enables semantic vector search.",
            "Machine learning powers recommendation systems."
        ]

        # Load embedding model
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Create embeddings
        self.embeddings = self.model.encode(self.documents)

        # Create FAISS index
        dimension = self.embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dimension)

        self.index.add(
            np.array(self.embeddings, dtype=np.float32)
        )

        # Neo4j connection from .env
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(
                os.getenv("NEO4J_USERNAME"),
                os.getenv("NEO4J_PASSWORD")
            )
        )

    # VECTOR SEARCH
    def vector_search(self, query, top_k=2):

        query_embedding = self.model.encode([query])

        distances, indices = self.index.search(
            np.array(query_embedding, dtype=np.float32),
            top_k
        )

        results = []

        for idx in indices[0]:
            results.append(self.documents[idx])

        return results

    # GRAPH SEARCH
    def graph_search(self, entity_name):
        query = """
        MATCH (a)-[r]->(b)
        WHERE toLower(b.name) CONTAINS toLower($name)
        OR toLower(a.name) CONTAINS toLower($name)

        RETURN coalesce(a.name, a.filename, a.id) AS source,
            type(r) AS relation,
            b.name AS target
        LIMIT 5
        """

        with self.driver.session() as session:
            result = session.run(query, name=entity_name)

            records = []
            for record in result:
                records.append(
                    f"{record['source']} -[{record['relation']}]-> {record['target']}"
                )

            return records

    # HYBRID SEARCH
    def hybrid_search(self, query):

        print("\nVector Search Results:\n")

        vector_results = self.vector_search(query)

        for result in vector_results:
            print(result)

        print("\nGraph Search Results:\n")

        words = query.split()

        found = False

        for word in words:

            graph_results = self.graph_search(word)

            if graph_results:

                found = True

                for item in graph_results:
                    print(item)

        if not found:
            print("No graph relationships found.")

    # CLOSE DRIVER
    def close(self):
        self.driver.close()


# RUN
if __name__ == "__main__":

    retriever = HybridRetriever()

    query = "Google Transformer"

    retriever.hybrid_search(query)

    retriever.close()