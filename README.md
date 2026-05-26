# 🧠 GraphRAG Knowledge Graph Agent

> **US-201 to US-206** — Archit Agrawal's implementation of the Knowledge Graph extraction pipeline.

A system that reads documents, extracts named entities and relationships using AI, and stores them as a connected **Knowledge Graph** in Neo4j.

---

## 📋 Tasks Implemented

| Task | Status | Description |
|---|---|---|
| **US-201** | ✅ Done | Document Ingestion Pipeline (PDF, DOCX, TXT) |
| **US-202** | ✅ Done | NER Pipeline using spaCy |
| **US-203** | ✅ Done | LLM-powered Relationship Extraction (Groq) |
| **US-204** | ✅ Done | Neo4j Database Setup & Connection |
| **US-205** | ✅ Done | Knowledge Graph Schema Design |
| **US-206** | ✅ Done | Populate Knowledge Graph |

---

## 🏗️ Architecture

```
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

## 🚀 Quick Start

### 1. Create Virtual Environment
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 3. Download spaCy Model
```powershell
# Large model (recommended, more accurate)
.venv\Scripts\python -m spacy download en_core_web_lg

# Small model (faster, less accurate)
.venv\Scripts\python -m spacy download en_core_web_sm
```

### 4. Configure Environment
Copy `.env.example` to `.env` and fill in your credentials:
```
GROQ_API_KEY=your_groq_key        # from console.groq.com
NEO4J_URI=bolt://localhost:7687    # or neo4j+s://xxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
```

### 5. Set Up Neo4j

**Option A — AuraDB (Free Cloud, Recommended):**
1. Go to [neo4j.com/cloud/aura](https://neo4j.com/cloud/aura)
2. Sign up free → Create a free instance
3. Copy `NEO4J_URI` and `NEO4J_PASSWORD` from the connection details

**Option B — Local Neo4j Desktop:**
1. Download from [neo4j.com/download](https://neo4j.com/download)
2. Install → Create a database → Start it
3. Use `bolt://localhost:7687`

### 6. Generate Demo Documents
```powershell
.venv\Scripts\python create_demo_docs.py
```

### 7. Run the Full Pipeline
```powershell
.venv\Scripts\python app.py
```

---

## 📂 Project Structure

```
8_GraphRAG_KG_Agent/
│
├── pipeline/
│   └── document_processor.py   # US-201: PDF/DOCX/TXT ingestion
│
├── extraction/
│   ├── ner.py                  # US-202: spaCy NER
│   └── llm_extractor.py        # US-203: Groq relationship extraction
│
├── graph/
│   ├── neo4j_connection.py     # US-204: Neo4j driver
│   ├── schema.py               # US-205: Node/edge schema
│   └── graph_builder.py        # US-206: Populate graph
│
├── tests/                      # Automated test suite
├── demo_docs/                  # Sample documents
├── app.py                      # Full pipeline demo
└── create_demo_docs.py         # Generates test documents
```

---

## 🧪 Running Tests

```powershell
# All tests (no Neo4j or Groq needed for most)
.venv\Scripts\python -m pytest tests/ -v

# Specific module
.venv\Scripts\python -m pytest tests/test_document_processor.py -v
.venv\Scripts\python -m pytest tests/test_ner.py -v
.venv\Scripts\python -m pytest tests/test_llm_extractor.py -v
.venv\Scripts\python -m pytest tests/test_schema.py -v
```

---

## 🔍 Query the Knowledge Graph

After running the pipeline, open [Neo4j Browser](https://browser.neo4j.io) and run:

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

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **spaCy** (`en_core_web_lg`) | Named Entity Recognition |
| **Groq** (Llama 3.1-8b) | LLM relationship extraction |
| **Neo4j** | Graph database |
| **LangChain** | LLM orchestration |
| **PyMuPDF** | PDF text extraction |
| **python-docx** | DOCX text extraction |
| **python-dotenv** | Secret management |
| **pytest** | Test suite |

---

## 📊 Knowledge Graph Schema

### Node Types
- `Document` — Source files
- `Person` — Named individuals
- `Organization` — Companies, institutions
- `Location` — Countries, cities, regions
- `Date` — Temporal references
- `Product` — Products, technologies
- `Event` — Named events
- `Concept` — Abstract ideas

### Relationship Types
- `MENTIONS` — Document → Entity
- `FOUNDED` — Person → Organization
- `WORKS_AT` — Person → Organization
- `LOCATED_IN` — Entity → Location
- `ACQUIRED` — Organization → Organization
- `APPEARS_WITH` — Entity ↔ Entity (co-occurrence)
- `RELATES_TO` — Generic relationship

---

## 🔐 Security

- API keys stored in `.env` (never committed)
- `.gitignore` protects `.env`, `.venv`, `__pycache__`
- Neo4j credentials loaded via `python-dotenv`
