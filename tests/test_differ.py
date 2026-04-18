"""Tests for csv_surgeon.differ."""
import pytest
from csv_surgeon.differ import unified_diff, only_changed, diff_summary


@pytest.fixture
def before_rows():
    return [
        {"id": "1", "name": "Alice", "score": "90"},
        {"id": "2", "name": "Bob",   "score": "80"},
        {"id": "3", "name": "Carol", "score": "70"},
    ]


@pytest.fixture
def after_rows():
    return [
        {"id": "1", "name": "Alice", "score": "95"},  # changed
        {"id": "2", "name": "Bob",   "score": "80"},  # unchanged
        {"id": "4", "name": "Dave",  "score": "60"},  # added
    ]


def test_unchanged_row_marked(before_rows, after_rows):
    result = {r["id"]: r for r in unified_diff(iter(before_rows), iter(after_rows), "id")}
    assert result["2"]["_diff_status"] == "unchanged"


def test_changed_row_marked(before_rows, after_rows):
    result = {r["id"]: r for r in unified_diff(iter(before_rows), iter(after_rows), "id")}
    assert result["1"]["_diff_status"] == "changed"


def test_removed_row_marked(before_rows, after_rows):
    result = {r["id"]: r for r in unified_diff(iter(before_rows), iter(after_rows), "id")}
    assert result["3"]["_diff_status"] == "removed"


def test_added_row_marked(before_rows, after_rows):
    result = {r["id"]: r for r in unified_diff(iter(before_rows), iter(after_rows), "id")}
    assert result["4"]["_diff_status"] == "added"


def test_only_changed_excludes_unchanged(before_rows, after_rows):
    diff = unified_diff(iter(before_rows), iter(after_rows), "id")
    result = list(only_changed(diff))
    statuses = {r["_diff_status"] for r in result}
    assert "unchanged" not in statuses
    assert len(result) == 3


def test_diff_summary_counts(before_rows, after_rows):
    diff = unified_diff(iter(before_rows), iter(after_rows), "id")
    summary = diff_summary(diff)
    assert summary["changed"] == 1
    assert summary["removed"] == 1
    assert summary["added"] == 1
    assert summary["unchanged"] == 1


def test_track_columns_limits_comparison():
    before = [{"id": "1", "name": "Alice", "note": "old"}]
    after  = [{"id": "1", "name": "Alice", "note": "new"}]
    result = list(unified_diff(iter(before), iter(after), "id", track_columns=["name"]))
    assert result[0]["_diff_status"] == "unchanged"


def test_empty_before():
    after = [{"id": "1", "name": "Alice"}]
    result = list(unified_diff(iter([]), iter(after), "id"))
    assert result[0]["_diff_status"] == "added"


def test_empty_after():
    before = [{"id": "1", "name": "Alice"}]
    result = list(unified_diff(iter(before), iter([]), "id"))
    assert result[0]["_diff_status"] == "removed"
