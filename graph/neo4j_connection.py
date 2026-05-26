"""
graph/neo4j_connection.py
US-204 — Neo4j Database Setup & Connection

Manages the Neo4j driver connection.
Supports both AuraDB (cloud) and local Neo4j Desktop.

Acceptance Criteria:
  - Neo4j database operational and connected
  - Install and configure Neo4j
"""

from __future__ import annotations

import os
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()


class Neo4jConnection:
    """
    US-204: Neo4j database connection manager.

    Handles:
      - Driver initialisation from .env credentials
      - Session context management
      - Connection health check
      - Query execution helpers

    Usage:
        conn = Neo4jConnection()
        conn.verify_connectivity()

        with conn.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS total")
            print(result.single()["total"])

        conn.close()
    """

    def __init__(
        self,
        uri:      Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """
        Args:
            uri:      Neo4j URI. Defaults to NEO4J_URI env var.
                      AuraDB:  neo4j+s://xxxx.databases.neo4j.io
                      Local:   bolt://localhost:7687
            username: Neo4j username. Defaults to NEO4J_USERNAME env var.
            password: Neo4j password. Defaults to NEO4J_PASSWORD env var.
        """
        self.uri      = uri      or os.getenv("NEO4J_URI",      "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME",  "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD",  "")
        self._driver  = None

        self._validate_config()

    # ── Public API ────────────────────────────────────────────────────────────

    def connect(self) -> None:
        """Initialise the Neo4j driver."""
        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise ImportError(
                "neo4j driver not installed.\n"
                "Run: .venv\\Scripts\\pip install neo4j"
            )

        self._driver = GraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password),
            max_connection_lifetime=300,
            max_connection_pool_size=50,
            connection_acquisition_timeout=30,
        )

    def verify_connectivity(self) -> bool:
        """
        Test that the database is reachable and credentials are valid.

        Returns:
            True if connection is successful.

        Raises:
            ConnectionError: If connection fails.
        """
        if self._driver is None:
            self.connect()

        try:
            self._driver.verify_connectivity()
            server_info = self._driver.get_server_info()
            print(f"  ✅ Connected to Neo4j")
            print(f"     URI:     {self.uri}")
            print(f"     Version: {server_info.agent}")
            return True
        except Exception as e:
            raise ConnectionError(
                f"❌ Failed to connect to Neo4j at {self.uri}\n"
                f"   Error: {e}\n\n"
                f"Troubleshooting:\n"
                f"  • AuraDB: Check NEO4J_URI, NEO4J_PASSWORD in .env\n"
                f"  • Local:  Make sure Neo4j Desktop is running\n"
                f"  • Local:  Default URI = bolt://localhost:7687\n"
                f"  • Local:  Default user = neo4j"
            ) from e

    @contextmanager
    def session(self, database: str = None):
        """
        Context manager for a Neo4j session.

        Usage:
            with conn.session() as session:
                session.run("MATCH (n) RETURN n LIMIT 10")
        """
        if self._driver is None:
            self.connect()

        kwargs = {}
        if database:
            kwargs["database"] = database

        with self._driver.session(**kwargs) as session:
            yield session

    def run_query(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results as a list of dicts.

        Args:
            cypher:     Cypher query string.
            parameters: Optional query parameters.

        Returns:
            List of result records as dicts.
        """
        with self.session() as session:
            result = session.run(cypher, parameters or {})
            return [dict(record) for record in result]

    def run_write(
        self,
        cypher: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Execute a write Cypher query (CREATE/MERGE/DELETE)."""
        with self.session() as session:
            session.run(cypher, parameters or {})

    def node_count(self) -> int:
        """Return total number of nodes in the database."""
        result = self.run_query("MATCH (n) RETURN count(n) AS total")
        return result[0]["total"] if result else 0

    def relationship_count(self) -> int:
        """Return total number of relationships in the database."""
        result = self.run_query("MATCH ()-[r]->() RETURN count(r) AS total")
        return result[0]["total"] if result else 0

    def health_check(self) -> Dict[str, Any]:
        """Return database statistics."""
        return {
            "nodes":         self.node_count(),
            "relationships": self.relationship_count(),
            "uri":           self.uri,
            "username":      self.username,
        }

    def clear_database(self, confirm: bool = False) -> None:
        """
        ⚠️  Delete ALL nodes and relationships.
        Requires confirm=True to prevent accidents.
        """
        if not confirm:
            raise ValueError(
                "clear_database requires confirm=True. "
                "This PERMANENTLY deletes all data!"
            )
        self.run_write("MATCH (n) DETACH DELETE n")
        print("🗑️  Database cleared.")

    def close(self) -> None:
        """Close the driver and release all connections."""
        if self._driver:
            self._driver.close()
            self._driver = None

    # ── Dunder ───────────────────────────────────────────────────────────────

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self) -> str:
        status = "connected" if self._driver else "disconnected"
        return f"Neo4jConnection(uri={self.uri!r}, status={status})"

    # ── Private ───────────────────────────────────────────────────────────────

    def _validate_config(self) -> None:
        """Validate that required config values are present."""
        if not self.uri:
            raise ValueError(
                "NEO4J_URI is not set.\n"
                "Add it to your .env file:\n"
                "  NEO4J_URI=bolt://localhost:7687"
            )
        if not self.password:
            print(
                "⚠️  NEO4J_PASSWORD is empty. "
                "Set it in .env if your database requires authentication."
            )


# ── Module-level singleton helper ─────────────────────────────────────────────

_connection: Optional[Neo4jConnection] = None


def get_connection() -> Neo4jConnection:
    """Return the module-level Neo4j connection (create if needed)."""
    global _connection
    if _connection is None:
        _connection = Neo4jConnection()
        _connection.connect()
    return _connection
