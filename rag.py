"""
rag.py - RAG pipeline: retrieval + LLM answer generation.

Combines get_top_chunks() with a local Foundry Local chat model
to produce grounded, context-based answers.

KAN-9:  Prompt engineering for Q&A
KAN-13: Integrate local LLM (Foundry Local)
KAN-15: Responsible outputs (fallback + source citations)
"""

from foundry_local_sdk.openai import ChatClient

from foundry import ensure_model
from retriever import get_top_chunks

CHAT_MODEL_ALIAS = "phi-3.5-mini"

# Minimum similarity score for a chunk to be considered relevant
RELEVANCE_THRESHOLD = 0.2

# Cached chat client (lazy init)
_chat_client: ChatClient | None = None


def _get_chat_client() -> ChatClient:
    """Initialize Foundry Local chat client (lazy, cached)."""
    global _chat_client
    if _chat_client is None:
        print(f"[rag] Loading chat model '{CHAT_MODEL_ALIAS}'...")
        model = ensure_model(CHAT_MODEL_ALIAS)
        _chat_client = model.get_chat_client()
        _chat_client.settings.temperature = 0.2
        _chat_client.settings.max_tokens = 512
        print("[rag] Chat model ready.")
    return _chat_client


SYSTEM_PROMPT = """You are a helpful Q&A assistant for the Microsoft Summer School on Foundry Local.
Answer the user's question using ONLY the context provided below.
If the answer cannot be found in the context, respond with:
"I don't have enough information to answer that question."
Do not make up or infer information beyond what is in the context.
Keep your answer concise (2-4 sentences). When the context comes from a named source, cite it as: "According to [Source Name], ..."
"""


def answer_query(question: str, top_k: int = 5, verbose: bool = False) -> str:
    """
    Full RAG pipeline: retrieve relevant chunks, then generate an answer.

    Args:
        question: The user's natural-language question.
        top_k:    Number of chunks to retrieve as context.
        verbose:  If True, print retrieved chunks for debugging.

    Returns:
        The model's answer as a string.
    """
    if not question.strip():
        return "Please enter a question."

    # Step 1 - Retrieve relevant chunks
    chunks = get_top_chunks(question, top_k=top_k)

    # Filter out low-relevance chunks
    relevant_chunks = [c for c in chunks if c["score"] >= RELEVANCE_THRESHOLD]

    if verbose:
        print("\n[rag] Retrieved chunks:")
        for i, c in enumerate(relevant_chunks, 1):
            print(f"  {i}. [{c['source']}] score={c['score']:.3f}")
            print(f"     {c['content'][:120]}...")

    # Step 2 - Build context string
    if not relevant_chunks:
        context = "(No relevant documents found)"
    else:
        context_parts = []
        for chunk in relevant_chunks:
            context_parts.append(f"[{chunk['source']}]\n{chunk['content']}")
        context = "\n\n---\n\n".join(context_parts)

    # Step 3 - Call the local LLM via native ChatClient
    client = _get_chat_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\nContext:\n{context}"},
        {"role": "user", "content": question},
    ]

    response = client.complete_chat(messages)
    return response.choices[0].message.content.strip()
