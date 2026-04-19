import pytest
from csv_surgeon.deduplicator_fuzzy import (
    fuzzy_deduplicate,
    fuzzy_deduplicate_sorted,
    _similarity,
)


# ---------------------------------------------------------------------------
# _similarity unit tests
# ---------------------------------------------------------------------------

def test_similarity_identical_strings():
    assert _similarity("hello", "hello") == 1.0


def test_similarity_completely_different():
    score = _similarity("abc", "xyz")
    assert score == 0.0


def test_similarity_empty_strings():
    assert _similarity("", "") == 1.0


def test_similarity_one_empty():
    assert _similarity("abc", "") == 0.0


def test_similarity_partial_overlap():
    score = _similarity("abc", "abc def")
    assert 0.0 < score < 1.0


# ---------------------------------------------------------------------------
# fuzzy_deduplicate
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice Smith", "city": "London"},
        {"name": "Alice Smyth", "city": "London"},   # near-duplicate
        {"name": "Bob Jones",   "city": "Paris"},
        {"name": "Bob Jones",   "city": "Paris"},    # exact duplicate
        {"name": "Carol White", "city": "Berlin"},
    ]


def test_fuzzy_deduplicate_removes_near_duplicate(sample_rows):
    result = list(fuzzy_deduplicate(sample_rows, columns=["name", "city"]))
    names = [r["name"] for r in result]
    assert "Alice Smyth" not in names


def test_fuzzy_deduplicate_keeps_first(sample_rows):
    result = list(fuzzy_deduplicate(sample_rows, columns=["name", "city"]))
    assert result[0]["name"] == "Alice Smith"


def test_fuzzy_deduplicate_removes_exact_duplicate(sample_rows):
    result = list(fuzzy_deduplicate(sample_rows, columns=["name", "city"]))
    bob_rows = [r for r in result if r["name"] == "Bob Jones"]
    assert len(bob_rows) == 1


def test_fuzzy_deduplicate_preserves_distinct_rows(sample_rows):
    result = list(fuzzy_deduplicate(sample_rows, columns=["name", "city"]))
    names = [r["name"] for r in result]
    assert "Carol White" in names


def test_fuzzy_deduplicate_low_threshold_removes_more():
    rows = [
        {"name": "John"},
        {"name": "Jane"},
    ]
    result = list(fuzzy_deduplicate(rows, columns=["name"], threshold=0.5))
    assert len(result) == 1


def test_fuzzy_deduplicate_high_threshold_keeps_all():
    rows = [
        {"name": "Alice"},
        {"name": "Bob"},
    ]
    result = list(fuzzy_deduplicate(rows, columns=["name"], threshold=0.99))
    assert len(result) == 2


def test_fuzzy_deduplicate_empty_input():
    result = list(fuzzy_deduplicate([], columns=["name"]))
    assert result == []


# ---------------------------------------------------------------------------
# fuzzy_deduplicate_sorted
# ---------------------------------------------------------------------------

def test_fuzzy_deduplicate_sorted_removes_adjacent_duplicate():
    rows = [
        {"val": "hello world"},
        {"val": "hello world"},
        {"val": "something else"},
    ]
    result = list(fuzzy_deduplicate_sorted(rows, columns=["val"]))
    assert len(result) == 2


def test_fuzzy_deduplicate_sorted_does_not_compare_non_adjacent():
    rows = [
        {"val": "hello world"},
        {"val": "something else"},
        {"val": "hello world"},
    ]
    result = list(fuzzy_deduplicate_sorted(rows, columns=["val"]))
    assert len(result) == 3


def test_fuzzy_deduplicate_sorted_empty_input():
    result = list(fuzzy_deduplicate_sorted([], columns=["val"]))
    assert result == []
