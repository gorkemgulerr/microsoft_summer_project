"""
main.py - Entry point for the Foundry Local RAG Assistant (CLI).

Starts an interactive Q&A loop. The user types a question and receives
an answer grounded in the local knowledge base.

Usage:
    python ingest.py   # run once to populate the knowledge base
    python main.py     # start the assistant

KAN-4:  RAG concept introduction
KAN-5:  Foundry Local environment
KAN-6:  Basic Python app structure
KAN-14: CLI user interface
"""

from db import init_db, count_chunks
from rag import answer_query

BANNER = """
╔══════════════════════════════════════════════════════════╗
║       Microsoft Summer School - Foundry Local RAG        ║
║              Local Q&A Assistant  (CLI)                  ║
╚══════════════════════════════════════════════════════════╝
Type your question and press Enter. Commands:
  /verbose  - toggle detailed retrieval output
  /quit     - exit the assistant
"""


def main():
    print(BANNER)

    # Ensure database exists
    init_db()
    chunk_count = count_chunks()

    if chunk_count == 0:
        print("[WARNING] Knowledge base is empty.")
        print("Please run:  python ingest.py\n")
        return

    print(f"Knowledge base loaded: {chunk_count} chunk(s) available.\n")

    verbose = False

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("/quit", "/exit", "exit", "quit"):
            print("Goodbye!")
            break

        if user_input.lower() == "/verbose":
            verbose = not verbose
            print(f"[Verbose mode {'ON' if verbose else 'OFF'}]\n")
            continue

        print("\nAssistant: ", end="", flush=True)
        answer = answer_query(user_input, verbose=verbose)
        print(answer)
        print()


if __name__ == "__main__":
    main()
