# Performance Notes

**Date:** 2026-08-14  
**Hardware:** Apple Silicon (macOS, CPU inference via Foundry Local)  
**Models:** `qwen3-embedding-0.6b` (retrieval) · `phi-3.5-mini` (generation)

## Measurement Method

`time.perf_counter()` wraps the full `answer_query()` call — embedding the query,
ranking chunks, building the context string, and calling the chat model.
First query includes model warm-up (cold start). Results logged to `performance_log.csv`.

## Raw Results

| Question (abbreviated) | Elapsed (s) | Chunks used |
|------------------------|-------------|-------------|
| What is RAG and what problem does it solve? | 28.69 | 5 |
| What are the three steps of the RAG pipeline? | 10.36 | 5 |
| What is Microsoft Foundry Local? | 8.16 | 5 |
| What is cosine similarity? | 11.25 | 5 |
| What is a system prompt? | 7.65 | 5 |
| What is the capital of France? (unanswerable) | 4.63 | 5 |

**Cold-start query:** 28.69 s (includes model download into memory)  
**Warm queries (2–6):** avg **8.41 s**, range 4.63–11.25 s

## Observations

- **Cold start dominates:** The first query loads both `qwen3-embedding-0.6b` and
  `phi-3.5-mini` into memory, adding ~20 s of overhead. Subsequent queries are
  served from the cached clients.

- **Unanswerable queries are faster:** "What is the capital of France?" completed in
  4.63 s. With low-relevance context, the model produces a short fallback rather
  than a detailed answer, reducing generation time.

- **Retrieval is not the bottleneck:** Cosine similarity over 29 chunks is near-instant.
  Virtually all latency comes from LLM inference (phi-3.5-mini on CPU).

- **Tuning levers:** To reduce latency, lower `max_tokens` (currently 512) or switch
  to a smaller model. Embedding latency is negligible at this knowledge base size.

## CSV Log

Raw measurements are written to `performance_log.csv` when `rag.PERF_LOG` is set:

```python
import rag
rag.PERF_LOG = "performance_log.csv"
```

`performance_log.csv` is excluded from the repository (listed in `.gitignore`).
