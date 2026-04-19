"""Integration tests: chain clamp + filter to enforce a valid score range."""
import pytest
from csv_surgeon.clipper import clamp_column, clip_below, clip_above
from csv_surgeon.filters import greater_than_or_equal, less_than_or_equal
from csv_surgeon.pipeline import FilterPipeline


def _make_rows():
    return [
        {"id": "1", "value": "-50"},
        {"id": "2", "value": "0"},
        {"id": "3", "value": "50"},
        {"id": "4", "value": "100"},
        {"id": "5", "value": "200"},
    ]


def test_clamp_then_all_values_in_range():
    rows = list(clamp_column(iter(_make_rows()), "value", min_value=0, max_value=100))
    for row in rows:
        assert 0 <= int(row["value"]) <= 100


def test_clip_below_then_clip_above_leaves_mid_values():
    rows = _make_rows()
    step1 = clip_below(iter(rows), "value", threshold=0, replacement="0")
    step2 = clip_above(step1, "value", threshold=100, replacement="100")
    result = list(step2)
    assert result[0]["value"] == "0"   # -50 -> 0
    assert result[4]["value"] == "100" # 200 -> 100
    assert result[2]["value"] == "50"  # unchanged


def test_clamp_preserves_all_rows():
    rows = list(clamp_column(iter(_make_rows()), "value", min_value=0, max_value=100))
    assert len(rows) == 5


def test_clamp_output_column_does_not_alter_source():
    rows = list(clamp_column(iter(_make_rows()), "value", min_value=0, max_value=100, output_column="clamped"))
    assert rows[0]["value"] == "-50"
    assert rows[0]["clamped"] == "0"


def test_clamp_preserves_all_columns():
    rows = list(clamp_column(iter(_make_rows()), "value", min_value=0, max_value=100))
    assert "id" in rows[0]
    assert "value" in rows[0]
