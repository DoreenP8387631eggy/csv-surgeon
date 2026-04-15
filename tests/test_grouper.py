"""Tests for csv_surgeon.grouper."""

import pytest
from csv_surgeon.grouper import (
    group_by,
    aggregate_groups,
    agg_count,
    agg_sum,
    agg_max,
    agg_min,
)


@pytest.fixture()
def sample_rows():
    return [
        {"dept": "eng",   "name": "Alice",   "salary": "90000"},
        {"dept": "eng",   "name": "Bob",     "salary": "85000"},
        {"dept": "hr",    "name": "Carol",   "salary": "70000"},
        {"dept": "hr",    "name": "Dave",    "salary": ""},
        {"dept": "sales", "name": "Eve",     "salary": "60000"},
    ]


# ---------------------------------------------------------------------------
# group_by
# ---------------------------------------------------------------------------

def test_group_by_creates_correct_number_of_groups(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    assert len(groups) == 3


def test_group_by_correct_row_counts(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    assert len(groups[("eng",)]) == 2
    assert len(groups[("hr",)]) == 2
    assert len(groups[("sales",)]) == 1


def test_group_by_preserves_row_content(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    names = [r["name"] for r in groups[("eng",)]]
    assert names == ["Alice", "Bob"]


def test_group_by_missing_column_uses_empty_string(sample_rows):
    groups = group_by(sample_rows, ["nonexistent"])
    # all rows have the same key
    assert len(groups) == 1
    assert len(groups[("",)]) == 5


def test_group_by_multi_column_key(sample_rows):
    rows = [
        {"dept": "eng", "level": "senior", "name": "Alice"},
        {"dept": "eng", "level": "junior", "name": "Bob"},
        {"dept": "eng", "level": "senior", "name": "Carol"},
    ]
    groups = group_by(rows, ["dept", "level"])
    assert len(groups[("eng", "senior")]) == 2
    assert len(groups[("eng", "junior")]) == 1


# ---------------------------------------------------------------------------
# aggregate_groups
# ---------------------------------------------------------------------------

def test_aggregate_groups_yields_one_row_per_group(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    result = list(aggregate_groups(groups, ["dept"], {"count": agg_count()}))
    assert len(result) == 3


def test_aggregate_groups_count_all(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    result = {r["dept"]: r["count"] for r in
              aggregate_groups(groups, ["dept"], {"count": agg_count()})}
    assert result["eng"] == "2"
    assert result["hr"] == "2"
    assert result["sales"] == "1"


def test_aggregate_groups_count_non_empty_column(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    result = {r["dept"]: r["c"] for r in
              aggregate_groups(groups, ["dept"], {"c": agg_count("salary")})}
    # hr has one empty salary
    assert result["hr"] == "1"


def test_aggregate_groups_sum(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    result = {r["dept"]: r["total"] for r in
              aggregate_groups(groups, ["dept"], {"total": agg_sum("salary")})}
    assert result["eng"] == "175000.0"
    assert result["hr"] == "70000.0"   # empty salary treated as 0


def test_aggregate_groups_max(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    result = {r["dept"]: r["max_sal"] for r in
              aggregate_groups(groups, ["dept"], {"max_sal": agg_max("salary")})}
    assert result["eng"] == "90000.0"


def test_aggregate_groups_min(sample_rows):
    groups = group_by(sample_rows, ["dept"])
    result = {r["dept"]: r["min_sal"] for r in
              aggregate_groups(groups, ["dept"], {"min_sal": agg_min("salary")})}
    assert result["eng"] == "85000.0"


def test_agg_min_empty_group_returns_empty_string():
    groups = {("x",): [{"salary": "abc"}]}
    result = list(aggregate_groups(groups, ["dept"], {"m": agg_min("salary")}))
    assert result[0]["m"] == ""
