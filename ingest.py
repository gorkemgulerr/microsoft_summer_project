"""
ingest.py - Data ingestion pipeline for the RAG knowledge base.

Reads .txt files from the docs/ folder, splits them into chunks,
generates embeddings via Foundry Local, and stores everything in SQLite.

Run this script once (or whenever documents change):
    python ingest.py

KAN-10: Knowledge base design & chunking strategy
KAN-11: Data ingestion pipeline (chunk, embed, store in SQLite)
"""

import os

from foundry import ensure_model
from db import init_db, clear_db, insert_chunk, count_chunks

DOCS_DIR = "docs"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

CHUNK_SEPARATOR = "\n\n"
MIN_CHUNK_LENGTH = 50


def load_documents(docs_dir: str) -> list[tuple[str, str]]:
    """
    Read all .txt files in docs_dir.
    Returns a list of (source_name, full_text) tuples.
    """
    documents = []
    for filename in sorted(os.listdir(docs_dir)):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(docs_dir, filename)
        with open(filepath, encoding="utf-8") as f:
            text = f.read()
        source = filename.replace(".txt", "").replace("_", " ").title()
        documents.append((source, text))
        print(f"  Loaded: {filename} → source='{source}'")
    return documents


def chunk_document(source: str, text: str) -> list[tuple[str, str]]:
    """
    Split a document into paragraph-level chunks.
    Skips the 'Source: ...' header and '---' separator if present.
    """
    lines = text.strip().splitlines()
    if lines and lines[0].startswith("Source:"):
        lines = lines[2:]  # skip "Source: ..." and "---"
    text_body = "\n".join(lines)

    raw_chunks = text_body.split(CHUNK_SEPARATOR)
    chunks = []
    for raw in raw_chunks:
        cleaned = raw.strip()
        if len(cleaned) >= MIN_CHUNK_LENGTH:
            chunks.append((source, cleaned))
    return chunks


def run_ingestion():
    """Main ingestion routine."""
    print("=== RAG Ingestion Pipeline ===\n")

    # 1. Initialize database
    init_db()
    clear_db()
    print("Database cleared and ready.\n")

    # 2. Load documents
    print("Loading documents from docs/...")
    documents = load_documents(DOCS_DIR)
    print(f"Loaded {len(documents)} document(s).\n")

    # 3. Chunk documents
    all_chunks: list[tuple[str, str]] = []
    for source, text in documents:
        chunks = chunk_document(source, text)
        all_chunks.extend(chunks)
    print(f"Created {len(all_chunks)} chunk(s) total.\n")

    # 4. Load Foundry Local embedding model
    print(f"Loading Foundry Local embedding model '{EMBEDDING_MODEL_ALIAS}'...")
    model = ensure_model(EMBEDDING_MODEL_ALIAS)
    embed_client = model.get_embedding_client()
    print("Embedding model ready.\n")

    # 5. Embed all chunks in one batch and store in SQLite
    print("Embedding and storing chunks...")
    sources = [c[0] for c in all_chunks]
    texts = [c[1] for c in all_chunks]

    response = embed_client.generate_embeddings(texts)
    sorted_data = sorted(response.data, key=lambda d: d.index)
    embeddings = [d.embedding for d in sorted_data]

    for source, content, embedding in zip(sources, texts, embeddings):
        insert_chunk(source, content, embedding)

    total = count_chunks()
    print(f"\nIngestion complete. {total} chunk(s) stored in 'knowledge.db'.")
    print("You can now run: python3 main.py")


if __name__ == "__main__":
    run_ingestion()
