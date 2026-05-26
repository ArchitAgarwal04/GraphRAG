"""
app.py — GraphRAG Knowledge Graph Agent
Demo runner that ties together all US-201 to US-206 components.

Run: python app.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def run_pipeline(file_paths: list, verbose: bool = True):
    """
    Full pipeline: Document → NER → LLM Extraction → Neo4j Graph

    Steps:
        US-201: Load and chunk documents
        US-202: Extract entities with spaCy NER
        US-203: Extract relationships with Groq LLM
        US-204: Connect to Neo4j
        US-205: Apply graph schema
        US-206: Populate knowledge graph
    """
    from pipeline.document_processor import DocumentProcessor
    from extraction.ner              import NERExtractor
    from extraction.llm_extractor    import LLMRelationExtractor
    from graph.neo4j_connection      import Neo4jConnection
    from graph.schema                import SchemaManager
    from graph.graph_builder         import GraphBuilder

    print("=" * 60)
    print("  🧠 GraphRAG Knowledge Graph Agent")
    print("=" * 60)

    # ── US-201: Document Ingestion ─────────────────────────────────
    print("\n📄 US-201: Loading documents...")
    processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
    segments  = processor.process_multiple(file_paths)
    print(f"  Total segments: {len(segments)}")

    if not segments:
        print("❌ No segments loaded. Exiting.")
        return

    # ── US-202: NER ────────────────────────────────────────────────
    print("\n🏷️  US-202: Running NER...")
    ner       = NERExtractor(model="en_core_web_lg")
    ner_results = ner.extract_from_segments(segments, verbose=verbose)
    all_entities = [e for entities in ner_results.values() for e in entities]
    print(ner.summary(all_entities))

    # ── US-203: LLM Relation Extraction ───────────────────────────
    print("\n🔗 US-203: Extracting relationships with LLM...")
    llm_extractor = LLMRelationExtractor()
    triples = llm_extractor.extract_from_segments(segments[:10], verbose=verbose)  # limit for demo
    print(llm_extractor.summary(triples))

    # ── US-204: Neo4j Connection ───────────────────────────────────
    print("\n🔌 US-204: Connecting to Neo4j...")
    conn = Neo4jConnection()
    conn.verify_connectivity()

    # ── US-205: Apply Schema ───────────────────────────────────────
    print("\n🔧 US-205: Applying Knowledge Graph schema...")
    schema = SchemaManager(conn)
    schema.apply(verbose=verbose)
    schema.verify(verbose=verbose)

    # ── US-206: Populate Graph ─────────────────────────────────────
    print("\n📥 US-206: Populating Knowledge Graph...")
    builder = GraphBuilder(conn)

    for filename, entities in ner_results.items():
        doc_triples = [t for t in triples if t.source_doc == filename]
        builder.build_from_extraction(
            filename=filename,
            filepath=filename,
            entities=entities,
            triples=doc_triples,
            verbose=verbose,
        )

    # ── Final Stats ────────────────────────────────────────────────
    stats = conn.health_check()
    print("\n" + "=" * 60)
    print("  ✅ Pipeline Complete!")
    print(f"  Total nodes         : {stats['nodes']}")
    print(f"  Total relationships : {stats['relationships']}")
    print("=" * 60)
    print("\n  🌐 View your graph at: https://browser.neo4j.io")
    print("  Query: MATCH (n) RETURN n LIMIT 50")

    conn.close()


if __name__ == "__main__":
    demo_docs = list(Path("demo_docs").glob("*.txt"))
    if not demo_docs:
        print("⚠️  No demo docs found. Creating sample docs first...")
        from create_demo_docs import create_demo_docs
        create_demo_docs()
        demo_docs = list(Path("demo_docs").glob("*.txt"))

    file_paths = [str(p) for p in demo_docs]
    print(f"Processing {len(file_paths)} document(s): {[p.name for p in demo_docs]}")
    run_pipeline(file_paths)
