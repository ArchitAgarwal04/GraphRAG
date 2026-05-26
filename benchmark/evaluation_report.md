# GraphRAG vs VectorRAG Evaluation Report

## Objective

The goal of this experiment is to compare traditional VectorRAG retrieval with Hybrid GraphRAG retrieval using vector search and knowledge graph traversal.

---

# System Overview

## VectorRAG

VectorRAG uses semantic similarity search based on embeddings generated using Sentence Transformers and indexed using FAISS.

### Components
- SentenceTransformer
- FAISS Vector Index
- Semantic Similarity Retrieval

---

## GraphRAG

GraphRAG combines:
- Vector Search
- Knowledge Graph Traversal
- Neo4j Relationship Retrieval

### Components
- SentenceTransformer
- FAISS
- Neo4j
- Hybrid Retrieval Engine

---

# Benchmark Dataset

A benchmark dataset of 50 reasoning questions was prepared covering:
- AI research
- Organizations
- Semantic retrieval
- Knowledge graphs
- Recommendation systems
- Graph traversal

---

# Experimental Setup

## Embedding Model
all-MiniLM-L6-v2

## Vector Database
FAISS

## Graph Database
Neo4j AuraDB

## Documents Indexed
2 demo documents

## Total Nodes
163

## Total Relationships
174

---

# Evaluation Metrics

| Metric | Description |
|---|---|
| Retrieval Accuracy | Correctness of retrieved results |
| Semantic Relevance | Relevance of retrieved documents |
| Relationship Awareness | Ability to retrieve connected entities |
| Multi-hop Retrieval | Ability to traverse graph relationships |

---

# Results

| Feature | VectorRAG | GraphRAG |
|---|---|---|
| Semantic Search | Good | Good |
| Relationship Retrieval | No | Yes |
| Multi-hop Reasoning | Limited | Supported |
| Graph Traversal | No | Yes |
| Context Awareness | Medium | High |
| Retrieval Flexibility | Medium | High |

---

# Observations

1. VectorRAG performs well for semantic similarity retrieval.

2. GraphRAG improves contextual understanding using graph traversal.

3. GraphRAG supports relationship-aware retrieval between entities.

4. Hybrid retrieval improves explainability and structured reasoning.

---

# Conclusion

The Hybrid GraphRAG system successfully combines vector retrieval and knowledge graph traversal.

Compared to traditional VectorRAG, GraphRAG provides:
- Better contextual retrieval
- Relationship-aware reasoning
- Improved multi-hop querying
- Structured knowledge representation

The project successfully demonstrates a working GraphRAG pipeline using:
- Neo4j
- FAISS
- Sentence Transformers
- Hybrid Retrieval