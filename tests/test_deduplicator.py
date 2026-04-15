"""Tests for csv_surgeon.deduplicator."""

import pytest
from csv_surgeon.deduplicator import deduplicate, deduplicate_sorted


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "name": "Alice", "city": "NYC"},
        {"id": "2", "name": "Bob",   "city": "LA"},
        {"id": "1", "name": "Alice", "city": "NYC"},  # full duplicate
        {"id": "3", "name": "Carol", "city": "NYC"},
        {"id": "2", "name": "Bob",   "city": "LA"},   # full duplicate
    ]


def test_deduplicate_all_columns_removes_full_duplicates(sample_rows):
    result = list(deduplicate(sample_rows))
    assert len(result) == 3


def test_deduplicate_all_columns_preserves_order(sample_rows):
    result = list(deduplicate(sample_rows))
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"
    assert result[2]["id"] == "3"


def test_deduplicate_by_key_column(sample_rows):
    result = list(deduplicate(sample_rows, key_columns=["id"]))
    assert len(result) == 3
    ids = [r["id"] for r in result]
    assert ids == ["1", "2", "3"]


def test_deduplicate_by_multiple_key_columns():
    rows = [
        {"first": "Alice", "last": "Smith", "age": "30"},
        {"first": "Alice", "last": "Smith", "age": "31"},  # same name, diff age
        {"first": "Bob",   "last": "Smith", "age": "25"},
    ]
    result = list(deduplicate(rows, key_columns=["first", "last"]))
    assert len(result) == 2
    assert result[0]["first"] == "Alice"
    assert result[1]["first"] == "Bob"


def test_deduplicate_empty_input():
    result = list(deduplicate([]))
    assert result == []


def test_deduplicate_no_duplicates(sample_rows):
    unique_rows = [sample_rows[0], sample_rows[1], sample_rows[3]]
    result = list(deduplicate(unique_rows))
    assert len(result) == 3


def test_deduplicate_invalid_key_column_raises():
    """deduplicate should raise KeyError when a key_column is not present in a row."""
    rows = [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]
    with pytest.raises(KeyError):
        list(deduplicate(rows, key_columns=["nonexistent"]))


def test_deduplicate_sorted_consecutive_only():
    rows = [
        {"id": "1", "val": "a"},
        {"id": "1", "val": "a"},  # consecutive duplicate
        {"id": "2", "val": "b"},
        {"id": "1", "val": "a"},  # non-consecutive — NOT removed
    ]
    result = list(deduplicate_sorted(rows, key_columns=["id"]))
    assert len(result) == 3
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"
    assert result[2]["id"] == "1"


def test_deduplicate_sorted_all_columns_consecutive():
    rows = [
        {"id": "1", "val": "x"},
        {"id": "1", "val": "x"},
        {"id": "2", "val": "y"},
    ]
    result = list(deduplicate_sorted(rows))
    assert len(result) == 2


def test_deduplicate_sorted_empty_input():
    result = list(deduplicate_sorted([]))
    assert result == []
