"""
graph/graph_builder.py
US-206 — Populate Knowledge Graph

Inserts extracted entities and relationships into Neo4j
using MERGE (upsert) to avoid duplicates.

Acceptance Criteria:
  - 500+ documents successfully indexed
  - Build graph population script
"""

from __future__ import annotations

import time
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from graph.neo4j_connection import Neo4jConnection

from graph.schema import get_node_label


class GraphBuilder:
    """
    US-206: Populates Neo4j with entities and relationships.

    Uses MERGE (upsert) so it's safe to run multiple times —
    existing nodes are updated, not duplicated.

    Pipeline:
        1. create_document_node()  → Document node
        2. upsert_entities()       → Entity nodes + MENTIONS edges
        3. upsert_triples()        → Relationship edges between entities
        4. create_cooccurrence()   → APPEARS_WITH edges (optional)

    Usage:
        builder = GraphBuilder(connection)
        builder.create_document_node("report.pdf", "/docs/report.pdf")
        builder.upsert_entities(entities, source_doc="report.pdf")
        builder.upsert_triples(triples)
    """

    def __init__(self, connection: "Neo4jConnection", batch_size: int = 100):
        """
        Args:
            connection: Neo4jConnection instance.
            batch_size: Number of nodes/edges per transaction batch.
        """
        self.conn       = connection
        self.batch_size = batch_size

    # ── US-206: Document Node ─────────────────────────────────────────────────

    def create_document_node(
        self,
        filename: str,
        filepath: str = "",
        metadata: dict = None,
    ) -> None:
        """
        Create or update a Document node in the graph.

        Args:
            filename: The document's file name (used as unique ID).
            filepath: Full path to the file.
            metadata: Optional extra properties (e.g., author, date).
        """
        props = {
            "id":          filename,
            "filename":    filename,
            "filepath":    filepath,
            "ingested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            **(metadata or {}),
        }

        cypher = """
        MERGE (d:Document {id: $id})
        SET d.filename    = $filename,
            d.filepath    = $filepath,
            d.ingested_at = $ingested_at
        RETURN d
        """
        self.conn.run_write(cypher, props)

    # ── US-206: Entity Nodes ──────────────────────────────────────────────────

    def upsert_entities(
        self,
        entities,             # List[Entity] from ner.py
        source_doc: str = "",
        verbose: bool = True,
    ) -> int:
        """
        Upsert Entity nodes into Neo4j and create MENTIONS relationships
        from the source Document to each Entity.

        Args:
            entities:   List of Entity objects from NERExtractor.
            source_doc: Document filename (for MENTIONS relationship).
            verbose:    Print progress.

        Returns:
            Number of entity nodes processed.
        """
        if not entities:
            return 0

        count = 0

        for i in range(0, len(entities), self.batch_size):
            batch = entities[i : i + self.batch_size]

            for ent in batch:
                node_label = get_node_label(ent.label)

                # MERGE on normalized_name + label to avoid duplicates
                cypher = f"""
                MERGE (e:Entity {{normalized_name: $normalized, label: $label}})
                SET e.name            = $name,
                    e.label           = $label,
                    e.normalized_name = $normalized
                WITH e
                CALL apoc.create.addLabels(e, [$node_label]) YIELD node
                RETURN node
                """

                # Fallback without APOC (most Community editions don't have it)
                cypher_no_apoc = f"""
                MERGE (e:{node_label} {{normalized_name: $normalized}})
                SET e.name            = $name,
                    e.label           = $label,
                    e.normalized_name = $normalized
                """

                params = {
                    "name":       ent.text,
                    "normalized": ent.normalized,
                    "label":      ent.label,
                    "node_label": node_label,
                }

                try:
                    self.conn.run_write(cypher, params)
                except Exception:
                    # Fallback if APOC not available
                    self.conn.run_write(cypher_no_apoc, params)

                # Create MENTIONS edge from Document → Entity
                if source_doc:
                    self._create_mentions(source_doc, ent.normalized, node_label)

                count += 1

            if verbose:
                print(
                    f"  Graph: upserted {min(i + self.batch_size, len(entities))}"
                    f"/{len(entities)} entities...",
                    end="\r",
                )

        if verbose:
            print(f"\n  ✅ Upserted {count} entity nodes")

        return count

    # ── US-206: Relationship Edges ────────────────────────────────────────────

    def upsert_triples(
        self,
        triples,           # List[Triple] from llm_extractor.py
        verbose: bool = True,
    ) -> int:
        """
        Upsert relationship edges between entities using LLM-extracted triples.

        Args:
            triples: List of Triple objects from LLMRelationExtractor.
            verbose: Print progress.

        Returns:
            Number of relationships processed.
        """
        if not triples:
            return 0

        count = 0

        for triple in triples:
            # Normalize relation type: uppercase, underscores
            relation = triple.relation.upper().replace(" ", "_").replace("-", "_")

            # Sanitize relation for Cypher (must be valid identifier)
            relation = "".join(
                c if c.isalnum() or c == "_" else "_"
                for c in relation
            )

            cypher = f"""
            MERGE (a:Entity {{normalized_name: $subj_norm}})
            ON CREATE SET a.name = $subj_name

            MERGE (b:Entity {{normalized_name: $obj_norm}})
            ON CREATE SET b.name = $obj_name

            MERGE (a)-[r:{relation}]->(b)
            SET r.source_doc  = $source_doc,
                r.source_text = $source_text,
                r.created_at  = $created_at
            """

            params = {
                "subj_norm":   triple.subject.lower().strip(),
                "subj_name":   triple.subject,
                "obj_norm":    triple.obj.lower().strip(),
                "obj_name":    triple.obj,
                "source_doc":  triple.source_doc,
                "source_text": triple.source_text[:200] if triple.source_text else "",
                "created_at":  time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }

            try:
                self.conn.run_write(cypher, params)
                count += 1
            except Exception as e:
                print(f"  ⚠️  Failed to write triple {triple}: {e}")

        if verbose:
            print(f"  ✅ Upserted {count} relationship edges")

        return count

    # ── US-206: Co-occurrence Edges ───────────────────────────────────────────

    def create_cooccurrence_edges(
        self,
        entities_per_segment: dict,  # {segment_id: [Entity, ...]}
        verbose: bool = True,
    ) -> int:
        """
        Create APPEARS_WITH edges between entities in the same text segment.
        Helps discover implicit relationships even without LLM extraction.

        Args:
            entities_per_segment: Dict mapping segment_id → list of entities.
            verbose: Print progress.

        Returns:
            Number of co-occurrence edges created.
        """
        count = 0

        for seg_id, entities in entities_per_segment.items():
            if len(entities) < 2:
                continue

            for i, ent_a in enumerate(entities):
                for ent_b in entities[i + 1:]:
                    if ent_a.normalized == ent_b.normalized:
                        continue

                    cypher = """
                    MERGE (a:Entity {normalized_name: $a_norm})
                    MERGE (b:Entity {normalized_name: $b_norm})
                    MERGE (a)-[r:APPEARS_WITH]->(b)
                    SET r.segment_id = $seg_id,
                        r.weight     = coalesce(r.weight, 0) + 1
                    """
                    params = {
                        "a_norm": ent_a.normalized,
                        "b_norm": ent_b.normalized,
                        "seg_id": str(seg_id),
                    }

                    try:
                        self.conn.run_write(cypher, params)
                        count += 1
                    except Exception:
                        pass

        if verbose:
            print(f"  ✅ Created {count} co-occurrence edges")

        return count

    # ── US-206: Full Pipeline Run ─────────────────────────────────────────────

    def build_from_extraction(
        self,
        filename: str,
        filepath: str,
        entities,        # List[Entity]
        triples,         # List[Triple]
        verbose: bool = True,
    ) -> dict:
        """
        Full graph population run for one document.

        Args:
            filename:  Document filename (unique ID).
            filepath:  Full path to document.
            entities:  NER entities extracted from document.
            triples:   LLM-extracted relationship triples.
            verbose:   Print progress.

        Returns:
            Summary dict with node/edge counts.
        """
        if verbose:
            print(f"\n📥 Building graph for: {filename}")

        # 1. Document node
        self.create_document_node(filename, filepath)

        # 2. Entity nodes
        entity_count = self.upsert_entities(entities, source_doc=filename, verbose=verbose)

        # 3. Relationship edges
        triple_count = self.upsert_triples(triples, verbose=verbose)

        stats = self.conn.health_check()
        summary = {
            "document":      filename,
            "entities_added": entity_count,
            "triples_added":  triple_count,
            "total_nodes":    stats["nodes"],
            "total_rels":     stats["relationships"],
        }

        if verbose:
            print(f"\n  📊 Graph Stats:")
            print(f"     Entities added : {entity_count}")
            print(f"     Triples added  : {triple_count}")
            print(f"     Total nodes    : {stats['nodes']}")
            print(f"     Total rels     : {stats['relationships']}")

        return summary

    # ── Private ───────────────────────────────────────────────────────────────

    def _create_mentions(
        self,
        doc_filename: str,
        entity_normalized: str,
        node_label: str,
    ) -> None:
        """Create a MENTIONS edge from Document → Entity."""
        cypher = f"""
        MATCH  (d:Document {{id: $doc_id}})
        MERGE  (e:{node_label} {{normalized_name: $ent_norm}})
        MERGE  (d)-[:MENTIONS]->(e)
        """
        try:
            self.conn.run_write(cypher, {
                "doc_id":   doc_filename,
                "ent_norm": entity_normalized,
            })
        except Exception:
            pass
