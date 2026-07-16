


# ❄️ Snowflake Docs  Assistant

A production-grade, modular **Hybrid RAG search engine** engineered to deliver precise, hallucination-free technical answers directly from official Snowflake documentation.

---

##  Tech Stack

| Layer | Technologies Used |
| --- | --- |
| **Backend & API** | **FastAPI** (Uvicorn), **Pydantic** |
| **RAG Orchestration** | **LangChain** (Chains, Document Transformers) |
| **Generative LLM** | **OpenAI GPT-4o-mini**  |
| **Vector Index** | **Pinecone** & **OpenAI Embeddings** (`text-embedding-3-small`) |
| **Hybrid Search** | **BM25 Retriever** (Exact Keyword Match) + **FlashRank** (Cross-Encoder Reranker) |
| **Ingestion Pipeline** | **AsyncHtmlLoader**, **BeautifulSoup**, **Html2Text** |
| **Frontend UI** | **HTML5**, **Java Script**, **CSS** |

---

##  System Pillars

* **Grounded Guardrails:** Programmed to output a strict, unified fallback message instead of guessing if documentation is missing.
* **4-Stage Hybrid Search:** Blends **BM25 keyword search** and **Pinecone semantic search** via Reciprocal Rank Fusion (RRF), finalized by a **FlashRank Cross-Encoder Reranker** for precise context targeting.
* **Separation of Concerns:** Clean separation of the crawler pipeline, prompt engineering layer, API orchestration layer, and static frontend UI.

---

##  4-Stage Retrieval Flow

```text
               [ User Query ]
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
   [ Stage 1: BM25 ]     [ Stage 2: Pinecone ]
   (Exact Match Index)   (Semantic Vector Match)
         │                       │
         └───────────┬───────────┘
                     ▼
         [ Stage 3: Ensemble (RRF) ]
            
                     │
                     ▼
         [ Stage 4: FlashRank Rerank ]
           (Top-5 Context Compression)

```

---

##  Project Structure

```text
├── data/scraped_docs.json   # Clean, parsed target markdown database
├── templates/index.html     # Decoupled responsive UI dashboard
├── src/
│   ├── app.py               # Fast API gateway & JSON orchestrator
│   ├── prompts.py           # Centralized system instructions
│   └── retriever.py         # Multi-layer hybrid search module
├── scraper.py               # Fast, async HTML web crawler
└── indexer.py               # Document splitter, embedder, & Pinecone loader

```



---

##  Setup & Run

### 1. Install Dependencies & Set Env

```bash
pip install -r requirements.txt

```

*Create a `.env` file with your `OPENAI_API_KEY`, `PINECONE_API_KEY`, and `PINECONE_INDEX_NAME`.*

### 2. Ingest Data & Index Vectors

```bash
python scraper.py && python indexer.py

```

### 3. Launch Web UI

```bash
uvicorn src.app:app --reload

```

 Open **`[http://127.0.0.1:8000](http://127.0.0.1:8000)`** in your browser.