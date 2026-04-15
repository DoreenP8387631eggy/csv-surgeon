"""Tests for csv_surgeon.comparer."""
import pytest
from csv_surgeon.comparer import diff_rows, intersect_rows, subtract_rows


@pytest.fixture
def left_rows():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob",   "score": "80"},
        {"id": "3", "name": "Carol", "score": "70"},
    ]


@pytest.fixture
def right_rows():
    return [
        {"id": "1", "name": "Alice", "score": "95"},  # changed score
        {"id": "3", "name": "Carol", "score": "70"},  # unchanged
        {"id": "4", "name": "Dave",  "score": "85"},  # added
    ]


# --- diff_rows ---

def test_diff_detects_removed_row(left_rows, right_rows):
    results = list(diff_rows(iter(left_rows), iter(right_rows), ["id"]))
    removed = [r for r in results if r["_diff"] == "removed"]
    assert len(removed) == 1
    assert removed[0]["id"] == "2"


def test_diff_detects_added_row(left_rows, right_rows):
    results = list(diff_rows(iter(left_rows), iter(right_rows), ["id"]))
    added = [r for r in results if r["_diff"] == "added"]
    assert len(added) == 1
    assert added[0]["id"] == "4"


def test_diff_detects_changed_row(left_rows, right_rows):
    results = list(diff_rows(iter(left_rows), iter(right_rows), ["id"]))
    changed = [r for r in results if r["_diff"] == "changed"]
    assert len(changed) == 1
    assert changed[0]["id"] == "1"
    assert changed[0]["score"] == "95"  # right-side value


def test_diff_unchanged_rows_not_yielded(left_rows, right_rows):
    results = list(diff_rows(iter(left_rows), iter(right_rows), ["id"]))
    ids = {r["id"] for r in results}
    assert "3" not in ids


def test_diff_empty_streams():
    results = list(diff_rows(iter([]), iter([]), ["id"]))
    assert results == []


def test_diff_identical_streams(left_rows):
    import copy
    results = list(diff_rows(iter(left_rows), iter(copy.deepcopy(left_rows)), ["id"]))
    assert results == []


def test_diff_composite_key():
    left = [{"a": "1", "b": "x", "v": "old"}]
    right = [{"a": "1", "b": "x", "v": "new"}]
    results = list(diff_rows(iter(left), iter(right), ["a", "b"]))
    assert len(results) == 1
    assert results[0]["_diff"] == "changed"


# --- intersect_rows ---

def test_intersect_returns_common_keys(left_rows, right_rows):
    results = list(intersect_rows(iter(left_rows), iter(right_rows), ["id"]))
    ids = {r["id"] for r in results}
    assert ids == {"1", "3"}


def test_intersect_uses_left_values(left_rows, right_rows):
    results = list(intersect_rows(iter(left_rows), iter(right_rows), ["id"]))
    alice = next(r for r in results if r["id"] == "1")
    assert alice["score"] == "90"  # left-side value preserved


def test_intersect_empty_right(left_rows):
    results = list(intersect_rows(iter(left_rows), iter([]), ["id"]))
    assert results == []


# --- subtract_rows ---

def test_subtract_excludes_right_keys(left_rows, right_rows):
    results = list(subtract_rows(iter(left_rows), iter(right_rows), ["id"]))
    ids = {r["id"] for r in results}
    assert ids == {"2"}


def test_subtract_empty_right_returns_all(left_rows):
    results = list(subtract_rows(iter(left_rows), iter([]), ["id"]))
    assert len(results) == len(left_rows)


def test_subtract_all_in_right_returns_empty(left_rows):
    import copy
    results = list(subtract_rows(iter(left_rows), iter(copy.deepcopy(left_rows)), ["id"]))
    assert results == []
