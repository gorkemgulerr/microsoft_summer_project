"""
db.py - SQLite database helpers for the RAG knowledge base.

Stores document chunks alongside their embedding vectors.
Embeddings are serialized as JSON text for simple retrieval.

KAN-8: SQLite storage
KAN-11: Data ingestion pipeline
"""

import sqlite3
import json

DB_PATH = "knowledge.db"


def init_db(db_path: str = DB_PATH):
    """Create the documents table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            source    TEXT NOT NULL,
            content   TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def clear_db(db_path: str = DB_PATH):
    """Remove all rows (used when re-ingesting documents)."""
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM documents")
    conn.commit()
    conn.close()


def insert_chunk(source: str, content: str, embedding: list[float], db_path: str = DB_PATH):
    """Insert a single document chunk with its embedding."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO documents (source, content, embedding) VALUES (?, ?, ?)",
        (source, content, json.dumps(embedding)),
    )
    conn.commit()
    conn.close()


def get_all_chunks(db_path: str = DB_PATH) -> list[dict]:
    """Return all stored chunks with their embeddings deserialized."""
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT id, source, content, embedding FROM documents")
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "source": row[1],
            "content": row[2],
            "embedding": json.loads(row[3]),
        }
        for row in rows
    ]


def count_chunks(db_path: str = DB_PATH) -> int:
    """Return the total number of stored chunks."""
    conn = sqlite3.connect(db_path)
    (count,) = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
    conn.close()
    return count
