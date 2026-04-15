"""Tests for csv_surgeon.sorter."""

import pytest
from csv_surgeon.sorter import sort_rows, sort_rows_multi


@pytest.fixture
def sample_rows():
    return [
        {"name": "Charlie", "age": "30", "score": "88.5"},
        {"name": "Alice",   "age": "25", "score": "95.0"},
        {"name": "Bob",     "age": "30", "score": "72.3"},
        {"name": "Diana",   "age": "22", "score": "88.5"},
    ]


def test_sort_rows_ascending_string(sample_rows):
    result = list(sort_rows(sample_rows, key="name"))
    names = [r["name"] for r in result]
    assert names == ["Alice", "Bob", "Charlie", "Diana"]


def test_sort_rows_descending_string(sample_rows):
    result = list(sort_rows(sample_rows, key="name", reverse=True))
    names = [r["name"] for r in result]
    assert names == ["Diana", "Charlie", "Bob", "Alice"]


def test_sort_rows_numeric_ascending(sample_rows):
    result = list(sort_rows(sample_rows, key="age", numeric=True))
    ages = [r["age"] for r in result]
    assert ages == ["22", "25", "30", "30"]


def test_sort_rows_numeric_descending(sample_rows):
    result = list(sort_rows(sample_rows, key="score", numeric=True, reverse=True))
    scores = [r["score"] for r in result]
    assert scores == ["95.0", "88.5", "88.5", "72.3"]


def test_sort_rows_non_numeric_sorted_last():
    rows = [
        {"val": "10"},
        {"val": "N/A"},
        {"val": "5"},
        {"val": ""},
    ]
    result = list(sort_rows(rows, key="val", numeric=True))
    numeric_vals = [r["val"] for r in result if r["val"] not in ("N/A", "")]
    non_numeric = [r["val"] for r in result if r["val"] in ("N/A", "")]
    assert numeric_vals == ["5", "10"]
    assert set(non_numeric) == {"N/A", ""}


def test_sort_rows_missing_key_treated_as_empty():
    rows = [{"name": "Zara"}, {"name": "Anna"}, {}]
    result = list(sort_rows(rows, key="name"))
    # empty string sorts before letters
    assert result[0].get("name", "") == ""


def test_sort_rows_does_not_mutate_original(sample_rows):
    original_first = sample_rows[0]["name"]
    list(sort_rows(sample_rows, key="name"))
    assert sample_rows[0]["name"] == original_first


def test_sort_rows_multi_primary_then_secondary(sample_rows):
    # Sort by age asc, then name asc — Charlie and Bob both have age 30
    result = list(sort_rows_multi(sample_rows, keys=[("age", False), ("name", False)]))
    age_30 = [r["name"] for r in result if r["age"] == "30"]
    assert age_30 == ["Bob", "Charlie"]


def test_sort_rows_multi_empty_keys(sample_rows):
    result = list(sort_rows_multi(sample_rows, keys=[]))
    assert result == sample_rows


def test_sort_rows_multi_single_key_descending(sample_rows):
    result = list(sort_rows_multi(sample_rows, keys=[("name", True)]))
    names = [r["name"] for r in result]
    assert names == ["Diana", "Charlie", "Bob", "Alice"]
