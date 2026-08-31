"""
api.py - Thin FastAPI layer over the existing RAG pipeline.

Wraps rag.answer_query() (retrieval + LLM generation) and exposes it over
HTTP for the frontend/. Does not modify db.py, rag.py, retriever.py, or
foundry.py - it only imports their existing public functions.

Run with:
    uvicorn api:app --reload --port 8000

KAN-16: Web API layer for the RAG assistant
"""

import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import count_chunks, init_db
from rag import RELEVANCE_THRESHOLD, answer_query
from retriever import get_top_chunks

app = FastAPI(title="Foundry Local RAG Assistant API")

# Allow the local Vite dev server (and its default alt port) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]
    elapsed_s: float


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/health")
def health():
    """Report knowledge base status: chunk count + ready/empty state."""
    chunk_count = count_chunks()
    return {
        "status": "ok" if chunk_count > 0 else "empty",
        "chunk_count": chunk_count,
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    """Answer a question using the existing RAG pipeline."""
    t_start = time.perf_counter()

    # Retrieve chunks separately (in addition to rag.answer_query()'s own
    # retrieval) purely to surface which sources were relevant to the caller;
    # rag.py itself is left untouched and only returns the answer text.
    chunks = get_top_chunks(req.question, top_k=5)
    relevant = [c for c in chunks if c["score"] >= RELEVANCE_THRESHOLD]
    sources = list(dict.fromkeys(c["source"] for c in relevant))

    answer = answer_query(req.question)

    elapsed = time.perf_counter() - t_start

    return AskResponse(answer=answer, sources=sources, elapsed_s=round(elapsed, 3))
