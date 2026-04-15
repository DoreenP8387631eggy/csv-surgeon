"""Tests for csv_surgeon.merger."""
import pytest
from csv_surgeon.merger import merge_rows, merge_rows_strict


@pytest.fixture
def stream_a():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
    ]


@pytest.fixture
def stream_b():
    return [
        {"id": "3", "name": "Carol"},
        {"id": "4", "name": "Dave"},
    ]


@pytest.fixture
def stream_extra_col():
    return [
        {"id": "5", "name": "Eve", "age": "30"},
    ]


def test_merge_rows_combines_all_rows(stream_a, stream_b):
    result = list(merge_rows([stream_a, stream_b]))
    assert len(result) == 4


def test_merge_rows_preserves_order(stream_a, stream_b):
    result = list(merge_rows([stream_a, stream_b]))
    assert result[0]["name"] == "Alice"
    assert result[2]["name"] == "Carol"


def test_merge_rows_empty_streams():
    result = list(merge_rows([]))
    assert result == []


def test_merge_rows_single_stream(stream_a):
    result = list(merge_rows([stream_a]))
    assert result == stream_a


def test_merge_rows_fills_missing_columns(stream_a, stream_extra_col):
    result = list(merge_rows([stream_a, stream_extra_col]))
    # stream_a rows should have 'age' filled with empty string
    assert result[0]["age"] == ""
    assert result[1]["age"] == ""
    # stream_extra_col row should have the age value intact
    assert result[2]["age"] == "30"


def test_merge_rows_custom_fill_value(stream_a, stream_extra_col):
    result = list(merge_rows([stream_a, stream_extra_col], fill_value="N/A"))
    assert result[0]["age"] == "N/A"


def test_merge_rows_unified_keys(stream_a, stream_extra_col):
    result = list(merge_rows([stream_a, stream_extra_col]))
    for row in result:
        assert set(row.keys()) == {"id", "name", "age"}


def test_merge_rows_strict_passes_identical_columns(stream_a, stream_b):
    result = list(merge_rows_strict([stream_a, stream_b]))
    assert len(result) == 4


def test_merge_rows_strict_raises_on_column_mismatch(stream_a, stream_extra_col):
    with pytest.raises(ValueError, match="columns"):
        list(merge_rows_strict([stream_a, stream_extra_col]))


def test_merge_rows_strict_empty():
    result = list(merge_rows_strict([]))
    assert result == []


def test_merge_rows_three_streams(stream_a, stream_b, stream_extra_col):
    result = list(merge_rows([stream_a, stream_b, stream_extra_col]))
    assert len(result) == 5
    assert result[4]["name"] == "Eve"
