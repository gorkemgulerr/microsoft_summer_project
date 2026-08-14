# Test Results

**Date:** 2026-08-14  
**Knowledge base:** 29 chunks (6 documents)  
**Models:** `qwen3-embedding-0.6b` (retrieval) · `phi-3.5-mini` (generation)

## Summary

| Category | Total | Passed | Failed |
|----------|-------|--------|--------|
| Answerable questions | 10 | 10 | 0 |
| Unanswerable questions | 4 | 4 | 0 |
| Edge cases | 3 | 3 | 0 |
| **Total** | **17** | **17** | **0** |

## Answerable Questions (should return a relevant answer)

| # | Question | Result |
|---|----------|--------|
| 1 | What is RAG and what problem does it solve? | PASS |
| 2 | What are the three steps of the RAG pipeline? | PASS |
| 3 | What is Microsoft Foundry Local? | PASS |
| 4 | How do I install Foundry Local? | PASS |
| 5 | What is cosine similarity? | PASS |
| 6 | What embedding model does Foundry Local recommend? | PASS |
| 7 | What is SQLite and why is it good for local apps? | PASS |
| 8 | What is a system prompt? | PASS |
| 9 | What chunking strategy should I use for RAG? | PASS |
| 10 | What Python commands do I type to ingest documents and start the assistant? | PASS |

## Unanswerable Questions (should return fallback)

The assistant correctly declines to answer questions outside its knowledge base.

| # | Question | Result |
|---|----------|--------|
| 1 | What is the capital of France? | PASS |
| 2 | Who won the FIFA World Cup in 2022? | PASS |
| 3 | What is the recipe for chocolate cake? | PASS |
| 4 | What is the population of Tokyo? | PASS |

## Edge Cases

| Label | Input | Result |
|-------|-------|--------|
| Empty input | `""` | PASS — returns "Please enter a question." (24 chars) |
| Single word | `"hello"` | PASS — returns graceful fallback (32 chars) |
| Very general | `"tell me everything"` | PASS — returns a bounded answer (928 chars) |

## Notes

- `RELEVANCE_THRESHOLD = 0.2`: chunks scoring below this are excluded from context.
- `top_k = 5`: up to 5 chunks retrieved per query.
- Question 6 ("What embedding model does Foundry Local recommend?") required increasing `top_k` from 3 to 5 to retrieve the relevant chunk — demonstrating the sensitivity of retrieval depth to knowledge base structure.
