from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

URI = os.getenv("NEO4J_URI")
USERNAME = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

# Connect to Neo4j
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

def get_connected_entities(entity_name):
    query = """
    MATCH (a)-[r]->(b)
    WHERE toLower(a.name) = toLower($name)
    RETURN a.name AS source,
           type(r) AS relationship,
           b.name AS target
    LIMIT 10
    """

    with driver.session() as session:
        results = session.run(query, name=entity_name)

        print(f"\nRelationships for: {entity_name}\n")

        found = False

        for record in results:
            found = True

            print(
                f"{record['source']} "
                f"-[{record['relationship']}]-> "
                f"{record['target']}"
            )

        if not found:
            print("No relationships found.")

if __name__ == "__main__":
    get_connected_entities("Google")