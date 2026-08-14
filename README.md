# Foundry Local RAG Assistant

A local Retrieval-Augmented Generation (RAG) Q&A assistant built for the **Microsoft Summer School – Foundry Local** program. Answers questions from a private knowledge base using on-device AI — no cloud, no API keys.

## How It Works

```
User Question
     │
     ▼
[Embedding Model]  ← Foundry Local (qwen3-embedding-0.6b)
     │  query vector
     ▼
[SQLite DB]  ← cosine similarity search → top-3 relevant chunks
     │
     ▼
[Chat Model]  ← Foundry Local (phi-3.5-mini)
     │  grounded answer
     ▼
  Answer
```

1. **Ingest**: Documents in `docs/` are chunked by paragraph, embedded, and stored in `knowledge.db` (SQLite).
2. **Retrieve**: The user's question is embedded and compared to all stored chunks via cosine similarity. The top-3 most relevant chunks are selected.
3. **Generate**: The local LLM (Phi-3.5 Mini) receives the retrieved chunks as context and generates a grounded answer. If the answer isn't in the context, it says so.

## Setup

```bash
# 1. Clone / download the project
cd microsoft-rag-assistant

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

## Running Tests

```bash
python tests/test_rag.py
```

## Project Structure

```
├── main.py          # CLI entry point
├── ingest.py        # Ingestion pipeline (chunk → embed → store)
├── rag.py           # answer_query(): retrieval + LLM generation
├── retriever.py     # get_top_chunks(): cosine similarity search
├── db.py            # SQLite helpers
├── requirements.txt
├── docs/            # Knowledge base (.txt files)
└── tests/
    └── test_rag.py  # Functional tests
```

## Design Decisions & Limitations

- **Storage**: SQLite with embeddings stored as JSON text. Simple and dependency-free. For larger knowledge bases (10,000+ chunks), a dedicated vector database (Chroma, Qdrant) would be faster.
- **Chunking**: Paragraph-level splits. Works well for structured text; may miss context for very short or very long paragraphs.
- **Relevance threshold**: Chunks with cosine similarity < 0.3 are excluded. Adjust `RELEVANCE_THRESHOLD` in `rag.py` if needed.
- **Models**: `qwen3-embedding-0.6b` (fast, compact) + `phi-3.5-mini` (good quality/speed balance). Larger models will give better answers but run slower.
- **Offline**: All inference runs locally. No data leaves the machine.

## References

- [Microsoft Learn: Build a RAG application](https://learn.microsoft.com/azure/ai-services/)
- [Foundry Local Documentation](https://learn.microsoft.com/windows/ai/foundry-local/)
- [Microsoft Tech Community: Building Your First Local RAG Application](https://techcommunity.microsoft.com/)
