import pytest
from csv_surgeon.reshaper import (
    reorder_columns,
    select_columns,
    drop_columns,
    move_column_first,
    move_column_last,
)


@pytest.fixture
def sample_rows():
    return [
        {"a": "1", "b": "2", "c": "3"},
        {"a": "4", "b": "5", "c": "6"},
    ]


def test_reorder_columns_changes_order(sample_rows):
    result = list(reorder_columns(iter(sample_rows), ["c", "b", "a"]))
    assert list(result[0].keys()) == ["c", "b", "a"]


def test_reorder_columns_preserves_values(sample_rows):
    result = list(reorder_columns(iter(sample_rows), ["c", "b", "a"]))
    assert result[0]["a"] == "1"
    assert result[0]["c"] == "3"


def test_reorder_columns_missing_column_gets_empty(sample_rows):
    result = list(reorder_columns(iter(sample_rows), ["a", "z"]))
    assert result[0]["z"] == ""


def test_select_columns_keeps_only_specified(sample_rows):
    result = list(select_columns(iter(sample_rows), ["a", "b"]))
    assert list(result[0].keys()) == ["a", "b"]
    assert "c" not in result[0]


def test_select_columns_preserves_values(sample_rows):
    result = list(select_columns(iter(sample_rows), ["a"]))
    assert result[1]["a"] == "4"


def test_drop_columns_removes_specified(sample_rows):
    result = list(drop_columns(iter(sample_rows), ["b"]))
    assert "b" not in result[0]
    assert "a" in result[0]
    assert "c" in result[0]


def test_drop_columns_missing_column_is_noop(sample_rows):
    result = list(drop_columns(iter(sample_rows), ["z"]))
    assert list(result[0].keys()) == ["a", "b", "c"]


def test_move_column_first_puts_column_at_front(sample_rows):
    result = list(move_column_first(iter(sample_rows), "c"))
    assert list(result[0].keys())[0] == "c"


def test_move_column_first_preserves_values(sample_rows):
    result = list(move_column_first(iter(sample_rows), "c"))
    assert result[0]["c"] == "3"
    assert result[0]["a"] == "1"


def test_move_column_first_missing_column_is_noop(sample_rows):
    result = list(move_column_first(iter(sample_rows), "z"))
    assert list(result[0].keys()) == ["a", "b", "c"]


def test_move_column_last_puts_column_at_end(sample_rows):
    result = list(move_column_last(iter(sample_rows), "a"))
    keys = list(result[0].keys())
    assert keys[-1] == "a"


def test_move_column_last_preserves_values(sample_rows):
    result = list(move_column_last(iter(sample_rows), "a"))
    assert result[0]["a"] == "1"


def test_move_column_last_missing_column_is_noop(sample_rows):
    result = list(move_column_last(iter(sample_rows), "z"))
    assert list(result[0].keys()) == ["a", "b", "c"]
