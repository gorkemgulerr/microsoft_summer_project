"""
tests/test_unit.py - Unit tests for pure-logic components.

Tests cosine similarity, document chunking, and SQLite helpers
without requiring Foundry Local, any model download, or a GPU.

Run with:
    pytest tests/test_unit.py
"""

import math
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retriever import _cosine_similarity
from ingest import chunk_document
from db import init_db, clear_db, insert_chunk, get_all_chunks, count_chunks


# ---------------------------------------------------------------------------
# _cosine_similarity
# ---------------------------------------------------------------------------

class TestCosineSimilarity:
    def test_identical_vectors(self):
        vec = [1.0, 2.0, 3.0]
        assert _cosine_similarity(vec, vec) == pytest.approx(1.0, abs=1e-6)

    def test_orthogonal_vectors(self):
        assert _cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0, abs=1e-6)

    def test_opposite_vectors(self):
        assert _cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0, abs=1e-6)

    def test_known_value(self):
        # [1,1] vs [1,0]: dot=1, |a|=sqrt(2), |b|=1 → 1/sqrt(2) ≈ 0.7071
        result = _cosine_similarity([1.0, 1.0], [1.0, 0.0])
        assert result == pytest.approx(1 / math.sqrt(2), abs=1e-6)

    def test_zero_vector_returns_zero(self):
        assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_longer_vectors(self):
        a = [0.5] * 100
        b = [0.5] * 100
        assert _cosine_similarity(a, b) == pytest.approx(1.0, abs=1e-6)

    def test_symmetry(self):
        a = [1.0, 2.0, 3.0]
        b = [4.0, 5.0, 6.0]
        assert _cosine_similarity(a, b) == pytest.approx(_cosine_similarity(b, a), abs=1e-9)


# ---------------------------------------------------------------------------
# chunk_document
# ---------------------------------------------------------------------------

class TestChunkDocument:
    def test_basic_chunking(self):
        p1 = "First paragraph with enough content to exceed the minimum chunk length filter."
        p2 = "Second paragraph with enough content to exceed the minimum chunk length filter."
        text = f"{p1}\n\n{p2}"
        chunks = chunk_document("Test", text)
        assert len(chunks) == 2
        assert chunks[0] == ("Test", p1)
        assert chunks[1] == ("Test", p2)

    def test_skips_source_header(self):
        text = "Source: Some Document\n---\nActual content paragraph here that is long enough."
        chunks = chunk_document("Test", text)
        assert len(chunks) == 1
        assert "Source:" not in chunks[0][1]
        assert "---" not in chunks[0][1]

    def test_filters_short_chunks(self):
        # MIN_CHUNK_LENGTH = 50; short paragraphs are skipped
        text = "Too short.\n\nThis paragraph is long enough to pass the minimum length filter easily."
        chunks = chunk_document("Test", text)
        assert len(chunks) == 1
        assert "long enough" in chunks[0][1]

    def test_source_name_preserved(self):
        text = "A sufficiently long paragraph that exceeds the minimum chunk length requirement."
        chunks = chunk_document("My Source", text)
        assert all(source == "My Source" for source, _ in chunks)

    def test_empty_text_returns_no_chunks(self):
        chunks = chunk_document("Test", "")
        assert chunks == []

    def test_multiple_paragraphs(self):
        paragraphs = [f"Paragraph number {i} with enough words to exceed the minimum length filter." for i in range(5)]
        text = "\n\n".join(paragraphs)
        chunks = chunk_document("Doc", text)
        assert len(chunks) == 5

    def test_chunk_content_stripped(self):
        text = "   Content with leading spaces that should be stripped cleanly.   \n\n   Another chunk here.   "
        chunks = chunk_document("Test", text)
        for _, content in chunks:
            assert content == content.strip()


# ---------------------------------------------------------------------------
# db helpers (isolated with a temp file)
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_db(tmp_path):
    """Provide a fresh temporary database path for each test."""
    db_file = str(tmp_path / "test.db")
    init_db(db_file)
    return db_file


class TestDatabase:
    def test_init_creates_table(self, tmp_db):
        # count_chunks should work on a freshly initialized db
        assert count_chunks(tmp_db) == 0

    def test_insert_and_count(self, tmp_db):
        insert_chunk("Source A", "Content A", [0.1, 0.2, 0.3], tmp_db)
        assert count_chunks(tmp_db) == 1

    def test_insert_multiple(self, tmp_db):
        for i in range(5):
            insert_chunk(f"Source {i}", f"Content {i}", [float(i)] * 3, tmp_db)
        assert count_chunks(tmp_db) == 5

    def test_get_all_chunks_returns_correct_fields(self, tmp_db):
        insert_chunk("TestSource", "TestContent", [1.0, 2.0], tmp_db)
        chunks = get_all_chunks(tmp_db)
        assert len(chunks) == 1
        chunk = chunks[0]
        assert chunk["source"] == "TestSource"
        assert chunk["content"] == "TestContent"
        assert chunk["embedding"] == [1.0, 2.0]
        assert "id" in chunk

    def test_embedding_round_trips_correctly(self, tmp_db):
        original = [0.123456789, -0.987654321, 0.5]
        insert_chunk("S", "C", original, tmp_db)
        chunks = get_all_chunks(tmp_db)
        assert chunks[0]["embedding"] == pytest.approx(original, abs=1e-9)

    def test_clear_db(self, tmp_db):
        insert_chunk("S", "C", [1.0], tmp_db)
        clear_db(tmp_db)
        assert count_chunks(tmp_db) == 0

    def test_clear_then_reinsert(self, tmp_db):
        insert_chunk("S", "C", [1.0], tmp_db)
        clear_db(tmp_db)
        insert_chunk("S2", "C2", [2.0], tmp_db)
        assert count_chunks(tmp_db) == 1
        assert get_all_chunks(tmp_db)[0]["source"] == "S2"

    def test_init_is_idempotent(self, tmp_db):
        # Calling init_db twice should not raise or duplicate anything
        init_db(tmp_db)
        init_db(tmp_db)
        assert count_chunks(tmp_db) == 0
