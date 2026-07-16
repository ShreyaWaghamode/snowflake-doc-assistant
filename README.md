# ❄️ Snowflake Docs Assistant

A production-grade, modular **Hybrid RAG search engine** engineered to deliver precise, hallucination-free technical answers directly from official Snowflake documentation.

---

##  Tech Stack

| Layer | Technologies Used |
| --- | --- |
| **Backend & API** | **FastAPI** (Uvicorn), **Pydantic**<br> |
| **RAG Orchestration** | **LangChain** (Chains, Document Transformers)

 |
| **Generative LLM** | **OpenAI GPT-4o-mini** (Deterministic: $temperature = 0.0$)

 |
| **Vector Index** | **Pinecone** & **OpenAI Embeddings** (`text-embedding-3-small`)

 |
| **Hybrid Search** | **BM25 Retriever** (Exact Keyword Match) + **FlashRank** (Cross-Encoder Reranker)

 |
| **Ingestion Pipeline** | **AsyncHtmlLoader**, **BeautifulSoup**, **Html2Text**<br> |
| **Frontend UI** | **HTML5**, **JavaScript**, **CSS**<br> |

---

##  System Pillars

* **Grounded Guardrails:** Programmed to output a strict, unified fallback message instead of guessing if documentation is missing.


* **4-Stage Hybrid Search:** Blends **BM25 keyword search** and **Pinecone semantic search** via Reciprocal Rank Fusion (RRF), finalized by a **FlashRank Cross-Encoder Reranker** for precise context targeting.


* **Separation of Concerns:** Clean separation of the crawler pipeline, prompt engineering layer, API orchestration layer, and static frontend UI.



---

```text
                        [ USER QUERY ]
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
   [ STAGE 1: LOCAL LAYER ]           [ STAGE 2: CLOUD LAYER ]
     BM25 Sparse Retriever              Pinecone Vector Store
      (Exact Keyword Match)            (Semantic Meaning Match)
            │                                   │
            └─────────────────┬─────────────────┘
                              ▼
                 [ STAGE 3: FUSION LAYER ]
                     EnsembleRetriever
              (Reciprocal Rank Fusion - RRF)
                              │
                              ▼
                [ STAGE 4: RERANKING LAYER ]
                 ContextualCompressionRetriever
                    (FlashRank Cross-Encoder)
                              │
                              ▼
                 [ FINAL TOP-5 CONTEXT CHUNKS ]
                     (Passed to GPT-4o-Mini)

```

---

## 📂 Project Structure

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
```[cite: 2, 5]

### 3. Launch Web UI

```bash
uvicorn src.app:app --reload

```

💻 Open **`[http://127.0.0.1:8000](http://127.0.0.1:8000)`** in your browser.