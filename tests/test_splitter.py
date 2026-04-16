"""Tests for csv_surgeon.splitter."""

import pytest
from csv_surgeon.splitter import split_by_count, split_by_column


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "dept": "eng", "name": "Alice"},
        {"id": "2", "dept": "eng", "name": "Bob"},
        {"id": "3", "dept": "hr",  "name": "Carol"},
        {"id": "4", "dept": "hr",  "name": "Dave"},
        {"id": "5", "dept": "fin", "name": "Eve"},
    ]


# --- split_by_count ---

def test_split_by_count_even_chunks(sample_rows):
    chunks = list(split_by_count(iter(sample_rows), 2))
    assert len(chunks) == 3
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 2
    assert len(chunks[2]) == 1  # remainder


def test_split_by_count_chunk_larger_than_input(sample_rows):
    chunks = list(split_by_count(iter(sample_rows), 100))
    assert len(chunks) == 1
    assert len(chunks[0]) == 5


def test_split_by_count_chunk_size_one(sample_rows):
    chunks = list(split_by_count(iter(sample_rows), 1))
    assert len(chunks) == 5
    for chunk in chunks:
        assert len(chunk) == 1


def test_split_by_count_empty_input():
    chunks = list(split_by_count(iter([]), 3))
    assert chunks == []


def test_split_by_count_invalid_chunk_size(sample_rows):
    with pytest.raises(ValueError, match="chunk_size must be >= 1"):
        list(split_by_count(iter(sample_rows), 0))


def test_split_by_count_negative_chunk_size(sample_rows):
    with pytest.raises(ValueError, match="chunk_size must be >= 1"):
        list(split_by_count(iter(sample_rows), -5))


def test_split_by_count_preserves_row_data(sample_rows):
    chunks = list(split_by_count(iter(sample_rows), 3))
    assert chunks[0][0]["name"] == "Alice"
    assert chunks[1][0]["name"] == "Dave"


def test_split_by_count_total_rows_preserved(sample_rows):
    """Ensure no rows are lost or duplicated across all chunks."""
    chunks = list(split_by_count(iter(sample_rows), 2))
    all_rows = [row for chunk in chunks for row in chunk]
    assert all_rows == sample_rows


# --- split_by_column ---

def test_split_by_column_groups_consecutive(sample_rows):
    groups = list(split_by_column(iter(sample_rows), "dept"))
    assert len(groups) == 3
    assert groups[0][0] == "eng"
    assert groups[1][0] == "hr"
    assert groups[2][0] == "fin"


def test_split_by_column_group_sizes(sample_rows):
    groups = list(split_by_column(iter(sample_rows), "dept"))
    assert len(groups[0][1]) == 2
    assert len(groups[1][1]) == 2
    assert len(groups[2][1]) == 1


def test_split_by_column_single_row_groups():
    rows = [
        {"k": "a", "v": "1"},
        {"k": "b", "v": "2"},
        {"k": "c", "v": "3"},
    ]
    groups = list(split_by_column(iter(rows), "k"))
    assert len(groups) == 3


def test_split_by_column_all_same_value(sample_rows):
    rows = [{"dept": "eng", "id": str(i)} for i in range(4)]
    groups = list(split_by_column(iter(rows), "dept"))
    assert len(groups) == 1
    assert groups[0][0] == "eng"
    assert len(groups[0][1]) == 4


def test_split_by_column_empty_input():
    groups = list(split_by_column(iter([]), "dept"))
    assert groups == []


def test_split_by_column_missing_column_raises():
    rows = [{"name": "Alice"}]
    with pytest.raises(KeyError):
        list(split_by_column(iter(rows), "dept"))
