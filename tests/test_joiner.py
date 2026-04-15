"""Tests for csv_surgeon.joiner module."""

import pytest
from csv_surgeon.joiner import inner_join, left_join


@pytest.fixture
def left_rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Charlie"},
    ]


@pytest.fixture
def right_rows():
    return [
        {"id": "1", "department": "Engineering"},
        {"id": "2", "department": "Marketing"},
        {"id": "4", "department": "HR"},
    ]


def test_inner_join_returns_only_matching_rows(left_rows, right_rows):
    result = list(inner_join(left_rows, right_rows, left_key="id"))
    assert len(result) == 2
    ids = {r["id"] for r in result}
    assert ids == {"1", "2"}


def test_inner_join_merges_columns(left_rows, right_rows):
    result = list(inner_join(left_rows, right_rows, left_key="id"))
    alice = next(r for r in result if r["id"] == "1")
    assert alice["name"] == "Alice"
    assert alice["department"] == "Engineering"


def test_inner_join_excludes_right_key_column(left_rows, right_rows):
    result = list(inner_join(left_rows, right_rows, left_key="id"))
    for row in result:
        assert list(row.keys()).count("id") == 1


def test_inner_join_prefix_on_collision():
    left = [{"id": "1", "name": "Alice", "note": "left"}]
    right = [{"id": "1", "note": "right"}]
    result = list(inner_join(left, right, left_key="id", right_prefix="r_"))
    assert result[0]["note"] == "left"
    assert result[0]["r_note"] == "right"


def test_left_join_returns_all_left_rows(left_rows, right_rows):
    result = list(left_join(left_rows, right_rows, left_key="id"))
    assert len(result) == 3


def test_left_join_enriches_matching_rows(left_rows, right_rows):
    result = list(left_join(left_rows, right_rows, left_key="id"))
    alice = next(r for r in result if r["id"] == "1")
    assert alice["department"] == "Engineering"


def test_left_join_keeps_unmatched_rows_without_right_columns(left_rows, right_rows):
    result = list(left_join(left_rows, right_rows, left_key="id"))
    charlie = next(r for r in result if r["id"] == "3")
    assert "department" not in charlie
    assert charlie["name"] == "Charlie"


def test_inner_join_different_key_names():
    left = [{"lid": "1", "val": "a"}, {"lid": "2", "val": "b"}]
    right = [{"rid": "1", "extra": "x"}, {"rid": "3", "extra": "z"}]
    result = list(inner_join(left, right, left_key="lid", right_key="rid"))
    assert len(result) == 1
    assert result[0]["extra"] == "x"


def test_inner_join_empty_right(left_rows):
    result = list(inner_join(left_rows, [], left_key="id"))
    assert result == []


def test_left_join_empty_right(left_rows):
    result = list(left_join(left_rows, [], left_key="id"))
    assert len(result) == 3
    for row in result:
        assert "department" not in row
