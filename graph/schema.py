"""
graph/schema.py
US-205 — Knowledge Graph Schema

Defines all node types, relationship types, constraints, and indexes.
Applies them to Neo4j to ensure data integrity and fast queries.

Acceptance Criteria:
  - Schema supports entities, properties, and relationships
  - 500+ documents successfully indexed (schema handles scale)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph.neo4j_connection import Neo4jConnection

# ── Node Labels ───────────────────────────────────────────────────────────────

NODE_LABELS = {
    "Document":     "A source document (PDF, DOCX, TXT)",
    "Entity":       "Generic named entity (base label)",
    "Person":       "A named person or character",
    "Organization": "A company, institution, or group",
    "Location":     "A geographic place (city, country, region)",
    "Date":         "A temporal reference",
    "Product":      "A named product, service, or technology",
    "Event":        "A named event (conference, war, launch, etc.)",
    "Concept":      "An abstract concept, topic, or theme",
    "Money":        "A monetary value or financial figure",
    "Quantity":     "A measurement or numeric quantity",
    "Law":          "A named law, regulation, or policy",
    "WorkOfArt":    "A book, film, song, or other creative work",
}

# ── Relationship Types ────────────────────────────────────────────────────────

RELATIONSHIP_TYPES = {
    # Document relationships
    "MENTIONS":         "Document mentions an entity",
    "CONTAINS":         "Document contains a segment",

    # Entity-Entity relationships (from LLM extraction)
    "RELATES_TO":       "Generic relationship between entities",
    "FOUNDED":          "Person or org founded another org",
    "FOUNDED_BY":       "Org was founded by a person",
    "WORKS_AT":         "Person works at an organization",
    "CEO_OF":           "Person is CEO of an organization",
    "ACQUIRED":         "Org acquired another org",
    "PARTNER_OF":       "Entities are partners",
    "LOCATED_IN":       "Entity is located in a place",
    "BORN_IN":          "Person born in a location or date",
    "DIED_IN":          "Person died in a location or date",
    "MEMBER_OF":        "Person is member of an organization",
    "SUBSIDIARY_OF":    "Org is subsidiary of another",
    "COMPETITOR_OF":    "Orgs are competitors",
    "INVESTED_IN":      "Entity invested in another",
    "COLLABORATED_WITH":"Entities collaborated",
    "DEVELOPED":        "Entity developed a product or technology",
    "USES":             "Entity uses a product or technology",
    "ATTENDED":         "Person attended an event or institution",
    "PARTICIPATED_IN":  "Entity participated in an event",

    # Temporal
    "HAPPENED_IN":      "Event happened at a date/time",
    "FOUNDED_IN_YEAR":  "Organization founded in a year",

    # Co-occurrence (from NER)
    "APPEARS_WITH":     "Entities appear together in the same text segment",
}

# ── Cypher Schema Statements ──────────────────────────────────────────────────

CONSTRAINTS = [
    # Uniqueness constraints (also creates indexes automatically)
    "CREATE CONSTRAINT doc_id IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE",
    "CREATE CONSTRAINT person_name IF NOT EXISTS FOR (p:Person) REQUIRE p.normalized_name IS UNIQUE",
    "CREATE CONSTRAINT org_name IF NOT EXISTS FOR (o:Organization) REQUIRE o.normalized_name IS UNIQUE",
    "CREATE CONSTRAINT location_name IF NOT EXISTS FOR (l:Location) REQUIRE l.normalized_name IS UNIQUE",
    "CREATE CONSTRAINT product_name IF NOT EXISTS FOR (p:Product) REQUIRE p.normalized_name IS UNIQUE",
    "CREATE CONSTRAINT event_name IF NOT EXISTS FOR (e:Event) REQUIRE e.normalized_name IS UNIQUE",
    "CREATE CONSTRAINT concept_name IF NOT EXISTS FOR (c:Concept) REQUIRE c.normalized_name IS UNIQUE",
    "CREATE CONSTRAINT entity_key IF NOT EXISTS FOR (e:Entity) REQUIRE (e.normalized_name, e.label) IS NODE KEY",
]

INDEXES = [
    # Text indexes for fast name searches
    "CREATE INDEX doc_filename IF NOT EXISTS FOR (d:Document) ON (d.filename)",
    "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
    "CREATE INDEX entity_label IF NOT EXISTS FOR (e:Entity) ON (e.label)",
]

# Friendly label readable names for display
SPACY_LABEL_TO_NODE = {
    "PERSON":      "Person",
    "ORG":         "Organization",
    "GPE":         "Location",       # Geopolitical entity
    "LOC":         "Location",
    "DATE":        "Date",
    "MONEY":       "Money",
    "PRODUCT":     "Product",
    "EVENT":       "Event",
    "WORK_OF_ART": "WorkOfArt",
    "LAW":         "Law",
    "NORP":        "Organization",   # Nationalities/groups → Organization
    "FAC":         "Location",       # Facilities → Location
    "LANGUAGE":    "Concept",
    "PERCENT":     "Quantity",
    "QUANTITY":    "Quantity",
    "TIME":        "Date",
    "CARDINAL":    "Quantity",
    "ORDINAL":     "Quantity",
}


class SchemaManager:
    """
    US-205: Manages the Knowledge Graph schema in Neo4j.

    Creates constraints and indexes needed for a robust,
    scalable knowledge graph.

    Usage:
        from graph.neo4j_connection import Neo4jConnection
        from graph.schema import SchemaManager

        conn   = Neo4jConnection()
        schema = SchemaManager(conn)
        schema.apply()
        schema.verify()
    """

    def __init__(self, connection: "Neo4jConnection"):
        self.conn = connection

    def apply(self, verbose: bool = True) -> None:
        """
        Apply all constraints and indexes to the Neo4j database.
        Safe to run multiple times (uses IF NOT EXISTS).
        """
        if verbose:
            print("🔧 Applying Knowledge Graph schema...")

        errors = []

        # Apply constraints
        for stmt in CONSTRAINTS:
            try:
                self.conn.run_write(stmt)
                if verbose:
                    label = stmt.split("FOR (")[1].split(")")[0].split(":")[-1]
                    print(f"  ✅ Constraint: {label}")
            except Exception as e:
                # Some older Neo4j versions don't support NODE KEY
                err = str(e)
                if "NODE KEY" in stmt and "edition" in err.lower():
                    # NODE KEY requires Enterprise; skip silently for Community
                    pass
                else:
                    errors.append(f"  ⚠️  {stmt[:60]}... → {e}")

        # Apply indexes
        for stmt in INDEXES:
            try:
                self.conn.run_write(stmt)
                if verbose:
                    prop = stmt.split("ON (")[-1].rstrip(")")
                    print(f"  ✅ Index: {prop}")
            except Exception as e:
                errors.append(f"  ⚠️  {stmt[:60]}... → {e}")

        if errors:
            for err in errors:
                print(err)
        elif verbose:
            print("  ✅ Schema applied successfully.")

    def verify(self, verbose: bool = True) -> dict:
        """
        Check current schema state in Neo4j.

        Returns:
            Dict with constraint count and index count.
        """
        try:
            constraints = self.conn.run_query("SHOW CONSTRAINTS")
            indexes     = self.conn.run_query("SHOW INDEXES")
        except Exception:
            constraints, indexes = [], []

        result = {
            "constraints": len(constraints),
            "indexes":     len(indexes),
        }

        if verbose:
            print(f"\n📋 Schema Status:")
            print(f"   Constraints : {result['constraints']}")
            print(f"   Indexes     : {result['indexes']}")

        return result

    def drop_all(self, confirm: bool = False) -> None:
        """⚠️  Drop ALL constraints and indexes. Requires confirm=True."""
        if not confirm:
            raise ValueError("drop_all requires confirm=True.")

        for stmt in CONSTRAINTS:
            name = stmt.split(" IF NOT EXISTS")[0].split("CONSTRAINT ")[1]
            try:
                self.conn.run_write(f"DROP CONSTRAINT {name} IF EXISTS")
            except Exception:
                pass

        for stmt in INDEXES:
            name = stmt.split(" IF NOT EXISTS")[0].split("INDEX ")[1]
            try:
                self.conn.run_write(f"DROP INDEX {name} IF EXISTS")
            except Exception:
                pass

        print("🗑️  All schema constraints and indexes dropped.")


def get_node_label(spacy_label: str) -> str:
    """
    Map a spaCy entity label to a Knowledge Graph node label.

    Args:
        spacy_label: e.g., "ORG", "PERSON", "GPE"

    Returns:
        Node label string, e.g., "Organization", "Person", "Location"
    """
    return SPACY_LABEL_TO_NODE.get(spacy_label.upper(), "Entity")
