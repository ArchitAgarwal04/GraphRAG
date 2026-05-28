# 🧠 GraphRAG Knowledge Graph Agent

> **US-201 to US-206** — Archit Agrawal's implementation of the Knowledge Graph extraction pipeline.

A system that reads documents, extracts named entities and relationships using AI, and stores them as a connected **Knowledge Graph** in Neo4j.

---

# 🔎 Advanced Retrieval & GraphRAG Interface

> **US-207 to US-211** — Bhawna's implementation for semantic retrieval, vector indexing, hybrid search, benchmarking, and interactive GraphRAG exploration.

This module extends the Knowledge Graph pipeline with semantic search, FAISS vector indexing, hybrid retrieval, benchmarking utilities, and a Streamlit-based GraphRAG dashboard for interactive exploration.

---

# 📋 Tasks Implemented

| Task | Status | Description |
|---|---|---|
| **US-201** | ✅ Done | Document Ingestion Pipeline (PDF, DOCX, TXT) |
| **US-202** | ✅ Done | NER Pipeline using spaCy |
| **US-203** | ✅ Done | LLM-powered Relationship Extraction (Groq) |
| **US-204** | ✅ Done | Neo4j Database Setup & Connection |
| **US-205** | ✅ Done | Knowledge Graph Schema Design |
| **US-206** | ✅ Done | Populate Knowledge Graph |
| **US-207** | ✅ Done | Vector Embedding Pipeline |
| **US-208** | ✅ Done | FAISS Vector Index Integration |
| **US-209** | ✅ Done | Hybrid Retrieval System |
| **US-210** | ✅ Done | Configurable GraphRAG Query Engine |
| **US-211** | ✅ Done | Streamlit Knowledge Explorer Dashboard |

---

# 🏗️ Core Knowledge Graph Architecture

```text
Document (PDF/DOCX/TXT)
        │
        ▼ US-201
  DocumentProcessor
  (chunks text into segments)
        │
        ├──────────────────┐
        ▼ US-202           ▼ US-203
   NERExtractor      LLMRelationExtractor
  (spaCy entities)   (Groq → JSON triples)
        │                  │
        └──────────┬───────┘
                   ▼ US-204 + US-205 + US-206
            Neo4j Knowledge Graph
         (nodes = entities, edges = relationships)
```

---

# 🏗️ Extended Retrieval Architecture

```text
Knowledge Graph + Documents
            │
            ▼
    Embedding Pipeline
    (text → vector embeddings)
            │
            ▼
       FAISS Index
    (semantic similarity)
            │
     ┌──────┴──────┐
     ▼             ▼
Graph Retrieval   Vector Retrieval
 (Neo4j)             (FAISS)
     │                 │
     └────────┬────────┘
              ▼
       Hybrid Retrieval
   (combined ranked results)
              │
              ▼
      GraphRAG Dashboard
   (interactive exploration)
```

---

# 🚀 Quick Start

## 1. Create Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

---

## 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

---

## 3. Download spaCy Model

```powershell
# Large model (recommended)
.venv\Scripts\python -m spacy download en_core_web_lg

# Small model (faster)
.venv\Scripts\python -m spacy download en_core_web_sm
```

---

## 4. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
GROQ_API_KEY=your_groq_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

---

# 🗄️ Neo4j Setup

## Option A — AuraDB (Recommended)

1. Create a free account at https://neo4j.com/cloud/aura
2. Create a free instance
3. Copy credentials into `.env`

---

## Option B — Local Neo4j Desktop

1. Download Neo4j Desktop
2. Create a database
3. Start database service
4. Use:

```env
NEO4J_URI=bolt://localhost:7687
```

---

# ▶️ Running the Project

## Generate Demo Documents

```powershell
.venv\Scripts\python create_demo_docs.py
```

---

## Run the Main Pipeline

```powershell
python app.py
```

---

## Launch Streamlit Dashboard

```powershell
streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

---

# 📂 Project Structure

```text
8_GraphRAG_KG_Agent/
│
├── pipeline/
│   └── document_processor.py
│
├── extraction/
│   ├── ner.py
│   └── llm_extractor.py
│
├── retrieval/
│   ├── graph_retrieval.py
│   ├── hybrid_retrieval1.py
│   └── configurable_retrieval.py
│
├── vector_index/
│   ├── embedding_pipeline.py
│   └── faiss_index.py
│
├── graph/
│   ├── neo4j_connection.py
│   ├── schema.py
│   ├── graph_builder.py
│   └── visualize.py
│
├── benchmark/
│   ├── benchmark_questions.txt
│   └── evaluation_report.md
│
├── demo_docs/
│
├── tests/
│
├── app.py
└── create_demo_docs.py
```

---

# 🔍 Retrieval Features

## Vector Retrieval
- Semantic search using embeddings
- FAISS-powered similarity matching
- Fast document chunk retrieval

---

## Graph Retrieval
- Neo4j relationship-based querying
- Entity-to-entity traversal
- Graph-aware context extraction

---

## Hybrid Retrieval
- Combines semantic + graph retrieval
- Improves contextual relevance
- Supports configurable ranking logic

---

# 🧪 Example Retrieval Execution

## Run Graph Retrieval

```powershell
python retrieval/graph_retrieval.py
```

---

## Run Hybrid Retrieval

```powershell
python retrieval/hybrid_retrieval1.py
```

---

## Run Configurable Retrieval

```powershell
python retrieval/configurable_retrieval.py
```

---

# 📊 Benchmarking

Benchmarking utilities are available inside the `benchmark/` folder.

### Included Files

- `benchmark_questions.txt`
- `evaluation_report.md`

These help evaluate:
- Retrieval relevance
- Semantic similarity quality
- Hybrid retrieval performance
- Graph-context accuracy

---

# 🖥️ Streamlit Dashboard Features

The interactive dashboard supports:

- Knowledge graph visualization
- Hybrid retrieval interface
- Semantic search exploration
- Graph relationship inspection
- Real-time retrieval experimentation
- Interactive GraphRAG navigation

---

# 🔍 Query the Knowledge Graph

After running the pipeline, open Neo4j Browser and run:

```cypher
-- See everything
MATCH (n) RETURN n LIMIT 50

-- Find all people
MATCH (p:Person) RETURN p.name

-- Who founded what?
MATCH (p:Person)-[:FOUNDED]->(o:Organization)
RETURN p.name, o.name

-- What does a document mention?
MATCH (d:Document)-[:MENTIONS]->(e)
RETURN d.filename, e.name, e.label
LIMIT 20

-- Find relationships between two entities
MATCH (a {name: "Elon Musk"})-[r]->(b)
RETURN a.name, type(r), b.name
```

---

# 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **spaCy** (`en_core_web_lg`) | Named Entity Recognition |
| **Groq** (Llama 3.1-8b) | LLM relationship extraction |
| **Neo4j** | Graph database |
| **LangChain** | LLM orchestration |
| **FAISS** | Vector similarity search |
| **Sentence Transformers** | Embedding generation |
| **Streamlit** | Interactive dashboard |
| **PyVis** | Graph visualization |
| **PyMuPDF** | PDF text extraction |
| **python-docx** | DOCX text extraction |
| **python-dotenv** | Secret management |
| **pytest** | Test suite |

---

# 📊 Knowledge Graph Schema

## Node Types

- `Document` — Source files
- `Person` — Named individuals
- `Organization` — Companies, institutions
- `Location` — Countries, cities, regions
- `Date` — Temporal references
- `Product` — Products, technologies
- `Event` — Named events
- `Concept` — Abstract ideas

---

## Relationship Types

- `MENTIONS` — Document → Entity
- `FOUNDED` — Person → Organization
- `WORKS_AT` — Person → Organization
- `LOCATED_IN` — Entity → Location
- `ACQUIRED` — Organization → Organization
- `APPEARS_WITH` — Entity ↔ Entity (co-occurrence)
- `RELATES_TO` — Generic relationship

---

# 🔐 Security

- API keys stored in `.env` (never committed)
- `.gitignore` protects `.env`, `.venv`, `__pycache__`
- Neo4j credentials loaded via `python-dotenv`

---

# 👨‍💻 Contributors

- **Archit Agrawal** — Core Knowledge Graph Pipeline (US-201 → US-206)
- **Bhawna** — Retrieval, Vector Search, Hybrid GraphRAG & Dashboard (US-207 → US-211)

---
