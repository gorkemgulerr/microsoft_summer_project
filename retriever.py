"""
retriever.py - Semantic retrieval using cosine similarity.

Embeds the user query with a Foundry Local embedding model, then ranks
all stored chunks by cosine similarity and returns the top-K most relevant.

KAN-7:  Embeddings & vector similarity
KAN-12: get_top_chunks() retrieval function
"""

import math
from foundry_local_sdk.openai import EmbeddingClient

from foundry import ensure_model
from db import get_all_chunks

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

# Cached embedding client (lazy init)
_embed_client: EmbeddingClient | None = None


def _get_embed_client() -> EmbeddingClient:
    """Initialize Foundry Local embedding client (lazy, cached)."""
    global _embed_client
    if _embed_client is None:
        print(f"[retriever] Loading embedding model '{EMBEDDING_MODEL_ALIAS}'...")
        model = ensure_model(EMBEDDING_MODEL_ALIAS)
        _embed_client = model.get_embedding_client()
        print("[retriever] Embedding model ready.")
    return _embed_client


def _embed(text: str) -> list[float]:
    """Generate an embedding vector for a single text string."""
    client = _get_embed_client()
    response = client.generate_embedding(text)
    return response.data[0].embedding


def _embed_batch(texts: list[str]) -> list[list[float]]:
    """Generate embedding vectors for a batch of texts."""
    client = _get_embed_client()
    response = client.generate_embeddings(texts)
    sorted_data = sorted(response.data, key=lambda d: d.index)
    return [d.embedding for d in sorted_data]


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def get_top_chunks(query: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve the top-K most relevant document chunks for the given query.

    Returns a list of dicts with keys: id, source, content, score.
    """
    query_embedding = _embed(query)
    chunks = get_all_chunks()

    if not chunks:
        return []

    scored = []
    for chunk in chunks:
        score = _cosine_similarity(query_embedding, chunk["embedding"])
        scored.append(
            {
                "id": chunk["id"],
                "source": chunk["source"],
                "content": chunk["content"],
                "score": score,
            }
        )

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def embed_texts_batch(texts: list[str]) -> list[list[float]]:
    """Public helper for ingest.py to embed many texts at once."""
    return _embed_batch(texts)
