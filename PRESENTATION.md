# Presentation: Foundry Local RAG Assistant

**Microsoft Summer School — Foundry Local**  
**Demo Day · 2026**

---

## Problem Statement

Large language models give confident-sounding answers even when they don't know
the correct answer — a phenomenon called *hallucination*. For domain-specific Q&A
(technical documentation, course materials, private knowledge bases), this is
unacceptable.

This project solves that by pairing a local LLM with a curated knowledge base:
the model is only allowed to answer from retrieved documents, and must say
"I don't have enough information" when the answer isn't there.

Everything runs **on-device** — no cloud calls, no API keys, no data leaving the machine.

---

## Key Features

| Feature | Detail |
|---------|--------|
| RAG pipeline | Retrieve → Augment → Generate, fully implemented in Python |
| Offline inference | Foundry Local runtime; models run on CPU/GPU locally |
| Semantic retrieval | `qwen3-embedding-0.6b` + cosine similarity over SQLite |
| Answer generation | `phi-3.5-mini` (~3.8B params), temperature=0.2 for consistency |
| Source citations | Model instructed to cite `[Source Name]` in every answer |
| Responsible fallback | Returns "I don't have enough information" when context is insufficient |
| Functional test suite | 17/17 tests pass (10 answerable, 4 unanswerable, 3 edge cases) |
| CI unit tests | 22 pytest unit tests run on GitHub Actions (no model required) |

---

## Live Demo

Sample Q&A from the functional test run (real output, unedited):

**Q: What is RAG and what problem does it solve?**
> RAG, or Retrieval-Augmented Generation, is a technique that enhances responses from
> large language models by retrieving relevant information from a document store.
> According to What Is Rag, it solves the problem of general LLMs lacking
> domain-specific or up-to-date knowledge by grounding answers in retrieved context,
> reducing hallucination.

**Q: What are the three steps of the RAG pipeline?**
> According to the provided context, the three steps of the RAG pipeline are:
> 1. Retrieve: Find the most relevant text chunks from a document store using semantic
>    similarity. 2. Augment: Add the retrieved chunks to the prompt as context.
> 3. Generate: Use the LLM to produce an answer grounded in that context.

**Q: What is the capital of France?** *(unanswerable — not in knowledge base)*
> I'm sorry, but the information provided does not contain the answer to your question.
> I don't have enough information to answer that question.

---

## Lessons Learned

1. **Chunking strategy directly determines retrieval quality.**  
   Early tests used `top_k=3`. Question 6 ("What embedding model does Foundry Local
   recommend?") consistently failed because the relevant chunk ranked 4th. Increasing
   `top_k` to 5 resolved it — but also meant the context window grew. The right value
   depends on document density, not just intuition.

2. **Relevance threshold tuning is non-trivial.**  
   The initial threshold of 0.3 was too strict: some valid answers were filtered out.
   After lowering to 0.2, all 10 answerable questions passed. However, too low a
   threshold risks including noisy context that confuses the model. Threshold choice
   should be validated against a labeled test set — not guessed.

3. **Model warm-up dominates first-query latency.**  
   The first query took ~28 s because both models had to be loaded into memory.
   Subsequent queries averaged ~8 s. For a production assistant, pre-loading models
   at startup (rather than on first request) eliminates this perceived slowness.
