# Foundry Local RAG Assistant

![tests](https://github.com/gorkemgulerr/microsoft_summer_project/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

A local Retrieval-Augmented Generation (RAG) Q&A assistant built for the **Microsoft Summer School – Foundry Local** program. Answers questions from a private knowledge base using on-device AI — no cloud, no API keys.

## How It Works

```
User Question
     │
     ▼
[Embedding Model]  ← Foundry Local (qwen3-embedding-0.6b)
     │  query vector
     ▼
[SQLite DB]  ← cosine similarity search → top-5 relevant chunks
     │
     ▼
[Chat Model]  ← Foundry Local (phi-3.5-mini)
     │  grounded answer
     ▼
  Answer
```

1. **Ingest**: Documents in `docs/` are chunked by paragraph, embedded, and stored in `knowledge.db` (SQLite).
2. **Retrieve**: The user's question is embedded and compared to all stored chunks via cosine similarity. The top-5 most relevant chunks are selected.
3. **Generate**: The local LLM (Phi-3.5 Mini) receives the retrieved chunks as context and generates a grounded answer. If the answer isn't in the context, it says so.

## Setup

```bash
# 1. Clone the project
git clone https://github.com/gorkemgulerr/microsoft_summer_project.git
cd microsoft_summer_project

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ingest the knowledge base (run once, or after adding new docs)
python ingest.py

# 5. Start the assistant
python main.py
```

## Usage

```
You: What is RAG?
Assistant: According to What Is Rag, RAG (Retrieval-Augmented Generation) is a technique ...

You: /verbose    ← toggle retrieval debug output
You: /quit       ← exit
```

Add your own documents as `.txt` files to the `docs/` folder, then re-run `python ingest.py`.

## Web Interface

A FastAPI backend (`api.py`) and a React + Vite + TypeScript frontend (`frontend/`) are
available as an alternative to the CLI. The backend is a thin layer over the existing
`rag.answer_query()` — it does not change any retrieval or generation logic.

**1. Start the backend** (from the project root, with the same virtual environment):

```bash
pip install -r requirements-api.txt
uvicorn api:app --reload --port 8000
```

This exposes:

- `POST /ask` — body `{"question": string}`, returns `{"answer": string, "sources": string[], "elapsed_s": number}`
- `GET /health` — returns `{"status": "ok" | "empty", "chunk_count": number}`

**2. Start the frontend** (in a separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open the printed local URL (default `http://localhost:5173`). The page checks backend
health on load and lets you ask questions against the live knowledge base; it also shows
the architecture, real test results, and real performance data documented below.

The backend's CORS policy allows `http://localhost:5173` and `http://127.0.0.1:5173` by
default (see `api.py`).

## Running Tests

### Unit tests (no Foundry Local required — runs in CI)

```bash
pip install -r requirements-dev.txt
pytest tests/test_unit.py -v
```

22 tests covering cosine similarity, document chunking, and SQLite helpers.

### Functional tests (requires local Foundry Local + downloaded models)

```bash
python tests/test_rag.py
```

> **Note:** `test_rag.py` requires a working Foundry Local installation with
> `qwen3-embedding-0.6b` and `phi-3.5-mini` downloaded. It is **not** run in CI.
> See [docs/test_results.md](docs/test_results.md) for the latest results.

## Test Results

See [docs/test_results.md](docs/test_results.md) — **17/17 tests passed** on 2026-08-14.

## Performance

See [docs/performance_notes.md](docs/performance_notes.md). Average warm-query response time: ~8.4 s on Apple Silicon (CPU inference).

Enable CSV logging in your session:

```python
import rag
rag.PERF_LOG = "performance_log.csv"
```

## Presentation

See [PRESENTATION.md](PRESENTATION.md) for the demo-day write-up: problem statement, key features, live demo transcript, and lessons learned.

## Project Structure

```
├── main.py                        # CLI entry point
├── ingest.py                      # Ingestion pipeline (chunk → embed → store)
├── rag.py                         # answer_query(): retrieval + LLM generation
├── retriever.py                   # get_top_chunks(): cosine similarity search
├── db.py                          # SQLite helpers
├── api.py                         # FastAPI layer over rag.py (POST /ask, GET /health)
├── frontend/                      # React + Vite + TypeScript web UI
├── requirements.txt               # Runtime dependencies (pinned)
├── requirements-dev.txt           # Dev dependencies (pytest)
├── requirements-api.txt           # Web API dependencies (fastapi, uvicorn)
├── LICENSE                        # MIT License
├── PRESENTATION.md                # Demo-day presentation
├── docs/
│   ├── what_is_rag.txt
│   ├── foundry_local_intro.txt
│   ├── embeddings_and_similarity.txt
│   ├── prompt_engineering.txt
│   ├── sqlite_guide.txt
│   ├── python_best_practices.txt
│   ├── test_results.md            # Functional test results
│   └── performance_notes.md      # Response time measurements
├── tests/
│   ├── test_unit.py               # Unit tests (CI-compatible, no model needed)
│   └── test_rag.py                # Functional tests (requires Foundry Local)
└── .github/
    └── workflows/
        └── tests.yml              # GitHub Actions CI (runs test_unit.py)
```

## Design Decisions & Limitations

- **Storage**: SQLite with embeddings stored as JSON text. Simple and dependency-free. For larger knowledge bases (10,000+ chunks), a dedicated vector database (Chroma, Qdrant) would be faster.
- **Chunking**: Paragraph-level splits. Works well for structured text; may miss context for very short or very long paragraphs.
- **Relevance threshold**: Chunks with cosine similarity < 0.2 are excluded. Adjust `RELEVANCE_THRESHOLD` in `rag.py` if needed.
- **Models**: `qwen3-embedding-0.6b` (fast, compact) + `phi-3.5-mini` (good quality/speed balance). Larger models will give better answers but run slower.
- **Offline**: All inference runs locally. No data leaves the machine.

## References

- [Microsoft Learn: Build a RAG application](https://learn.microsoft.com/azure/ai-services/)
- [Foundry Local Documentation](https://learn.microsoft.com/windows/ai/foundry-local/)
- [Microsoft Tech Community: Building Your First Local RAG Application](https://techcommunity.microsoft.com/)
