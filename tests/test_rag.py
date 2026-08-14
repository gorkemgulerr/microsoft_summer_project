"""
tests/test_rag.py - Functional test suite for the RAG assistant.

Tests cover:
  - Answerable questions (should return a relevant answer)
  - Unanswerable questions (should return the fallback message)
  - Edge cases (empty input, very general questions)

KAN-16: Functional testing (test cases + edge cases)
KAN-18: Evaluation & improvement pass

Run with:
    python tests/test_rag.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import init_db, count_chunks
from rag import answer_query

FALLBACK_PHRASES = [
    "i don't have enough information",
    "i don't have that information",
    "cannot be found",
    "not in the context",
    "i'm sorry, but i don't have",
    "i don't have the specific",
    "i do not have enough",
    "no information available",
]

# --- Test cases ---

ANSWERABLE_QUESTIONS = [
    "What is RAG and what problem does it solve?",
    "What are the three steps of the RAG pipeline?",
    "What is Microsoft Foundry Local?",
    "How do I install Foundry Local?",
    "What is cosine similarity?",
    "What embedding model does Foundry Local recommend?",
    "What is SQLite and why is it good for local apps?",
    "What is a system prompt?",
    "What chunking strategy should I use for RAG?",
    "What Python commands do I type to ingest documents and start the assistant?",
]

UNANSWERABLE_QUESTIONS = [
    "What is the capital of France?",
    "Who won the FIFA World Cup in 2022?",
    "What is the recipe for chocolate cake?",
    "What is the population of Tokyo?",
]

EDGE_CASES = [
    ("empty input", ""),
    ("single word", "hello"),
    ("very general", "tell me everything"),
]


def check_fallback(answer: str) -> bool:
    answer_lower = answer.lower()
    return any(phrase in answer_lower for phrase in FALLBACK_PHRASES)


def run_tests():
    print("=== RAG Functional Test Suite ===\n")

    init_db()
    chunks = count_chunks()
    if chunks == 0:
        print("ERROR: Knowledge base is empty. Run 'python ingest.py' first.")
        sys.exit(1)
    print(f"Knowledge base: {chunks} chunks\n")

    results = {"passed": 0, "failed": 0, "total": 0}

    # --- Answerable questions ---
    print("--- Answerable Questions (should return a relevant answer) ---")
    for question in ANSWERABLE_QUESTIONS:
        results["total"] += 1
        answer = answer_query(question, verbose=False)
        is_fallback = check_fallback(answer)
        status = "FAIL (got fallback)" if is_fallback else "PASS"
        if not is_fallback:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  [{status}] {question[:60]}")
        if is_fallback:
            print(f"         Answer: {answer[:100]}")
    print()

    # --- Unanswerable questions ---
    print("--- Unanswerable Questions (should return fallback) ---")
    for question in UNANSWERABLE_QUESTIONS:
        results["total"] += 1
        answer = answer_query(question, verbose=False)
        is_fallback = check_fallback(answer)
        status = "PASS" if is_fallback else "FAIL (did not fall back)"
        if is_fallback:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print(f"  [{status}] {question[:60]}")
        if not is_fallback:
            print(f"         Answer: {answer[:100]}")
    print()

    # --- Edge cases ---
    print("--- Edge Cases ---")
    for label, question in EDGE_CASES:
        results["total"] += 1
        try:
            answer = answer_query(question, verbose=False)
            print(f"  [PASS] {label}: returned answer (len={len(answer)})")
            results["passed"] += 1
        except Exception as e:
            print(f"  [FAIL] {label}: raised exception: {e}")
            results["failed"] += 1
    print()

    # --- Summary ---
    print("=== Results ===")
    print(f"  Passed: {results['passed']} / {results['total']}")
    print(f"  Failed: {results['failed']} / {results['total']}")
    if results["failed"] == 0:
        print("  All tests passed!")
    else:
        print("  Some tests failed — review prompts or retrieval threshold.")


if __name__ == "__main__":
    run_tests()
