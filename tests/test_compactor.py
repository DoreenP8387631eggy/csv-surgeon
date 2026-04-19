"""Tests for csv_surgeon/compactor.py"""
import pytest
from csv_surgeon.compactor import compact_columns, compact_first_valid, drop_empty_columns


@pytest.fixture
def sample_rows():
    return [
        {"a": "foo", "b": "", "c": "bar"},
        {"a": "", "b": "baz", "c": ""},
        {"a": "x", "b": "y", "c": "z"},
    ]


def test_compact_columns_joins_non_empty(sample_rows):
    result = list(compact_columns(sample_rows, columns=["a", "b", "c"]))
    assert result[0]["compacted"] == "foo,bar"


def test_compact_columns_all_empty_gives_empty(sample_rows):
    rows = [{"a": "", "b": "", "c": ""}]
    result = list(compact_columns(rows, columns=["a", "b", "c"]))
    assert result[0]["compacted"] == ""


def test_compact_columns_custom_separator(sample_rows):
    result = list(compact_columns(sample_rows, columns=["a", "b", "c"], separator=" | "))
    assert result[2]["compacted"] == "x | y | z"


def test_compact_columns_keep_empty():
    rows = [{"a": "foo", "b": "", "c": "bar"}]
    result = list(compact_columns(rows, columns=["a", "b", "c"], skip_empty=False))
    assert result[0]["compacted"] == "foo,,bar"


def test_compact_columns_preserves_original_fields(sample_rows):
    result = list(compact_columns(sample_rows, columns=["a", "b"]))
    assert "c" in result[0]
    assert result[0]["c"] == "bar"


def test_compact_columns_custom_output_col(sample_rows):
    result = list(compact_columns(sample_rows, columns=["a", "b"], output_col="merged"))
    assert "merged" in result[0]


def test_compact_first_valid_picks_first(sample_rows):
    result = list(compact_first_valid(sample_rows, columns=["a", "b", "c"]))
    assert result[0]["compacted"] == "foo"
    assert result[1]["compacted"] == "baz"


def test_compact_first_valid_default_when_all_empty():
    rows = [{"a": "", "b": ""}]
    result = list(compact_first_valid(rows, columns=["a", "b"], default="N/A"))
    assert result[0]["compacted"] == "N/A"


def test_compact_first_valid_preserves_fields(sample_rows):
    result = list(compact_first_valid(sample_rows, columns=["a", "b"]))
    assert "c" in result[0]


def test_drop_empty_columns_removes_all_empty_col():
    rows = [
        {"name": "Alice", "ghost": ""},
        {"name": "Bob", "ghost": ""},
    ]
    result = list(drop_empty_columns(rows, columns=["ghost"]))
    assert "ghost" not in result[0]


def test_drop_empty_columns_keeps_non_empty_col():
    rows = [
        {"name": "Alice", "tag": "x"},
        {"name": "Bob", "tag": ""},
    ]
    result = list(drop_empty_columns(rows, columns=["tag"]))
    assert "tag" in result[0]


def test_drop_empty_columns_empty_stream():
    result = list(drop_empty_columns(iter([])))
    assert result == []
