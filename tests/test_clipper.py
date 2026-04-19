import pytest
from csv_surgeon.clipper import clamp_column, clip_below, clip_above


@pytest.fixture
def sample_rows():
    return [
        {"name": "alice", "score": "5"},
        {"name": "bob", "score": "15"},
        {"name": "carol", "score": "-3"},
        {"name": "dave", "score": "100"},
        {"name": "eve", "score": "bad"},
    ]


def apply(fn, rows):
    return list(fn(iter(rows)))


# clamp_column tests

def test_clamp_column_min(sample_rows):
    result = list(clamp_column(iter(sample_rows), "score", min_value=0))
    assert result[2]["score"] == "0"  # -3 clamped to 0


def test_clamp_column_max(sample_rows):
    result = list(clamp_column(iter(sample_rows), "score", max_value=50))
    assert result[3]["score"] == "50"  # 100 clamped to 50


def test_clamp_column_both(sample_rows):
    result = list(clamp_column(iter(sample_rows), "score", min_value=0, max_value=20))
    assert result[0]["score"] == "5"
    assert result[1]["score"] == "15"
    assert result[2]["score"] == "0"
    assert result[3]["score"] == "20"


def test_clamp_non_numeric_passes_through(sample_rows):
    result = list(clamp_column(iter(sample_rows), "score", min_value=0, max_value=20))
    assert result[4]["score"] == "bad"


def test_clamp_missing_column_is_noop(sample_rows):
    result = list(clamp_column(iter(sample_rows), "missing", min_value=0))
    assert result[0] == sample_rows[0]


def test_clamp_output_column(sample_rows):
    result = list(clamp_column(iter(sample_rows), "score", min_value=0, output_column="clamped"))
    assert "clamped" in result[0]
    assert result[0]["score"] == "5"  # original unchanged


def test_clamp_preserves_other_fields(sample_rows):
    result = list(clamp_column(iter(sample_rows), "score", min_value=0))
    assert result[0]["name"] == "alice"


# clip_below tests

def test_clip_below_replaces_low_values(sample_rows):
    result = list(clip_below(iter(sample_rows), "score", threshold=0, replacement="N/A"))
    assert result[2]["score"] == "N/A"


def test_clip_below_keeps_values_above_threshold(sample_rows):
    result = list(clip_below(iter(sample_rows), "score", threshold=0, replacement="N/A"))
    assert result[0]["score"] == "5"


def test_clip_below_non_numeric_unchanged(sample_rows):
    result = list(clip_below(iter(sample_rows), "score", threshold=0, replacement="N/A"))
    assert result[4]["score"] == "bad"


# clip_above tests

def test_clip_above_replaces_high_values(sample_rows):
    result = list(clip_above(iter(sample_rows), "score", threshold=50, replacement="MAX"))
    assert result[3]["score"] == "MAX"


def test_clip_above_keeps_values_below_threshold(sample_rows):
    result = list(clip_above(iter(sample_rows), "score", threshold=50, replacement="MAX"))
    assert result[1]["score"] == "15"


def test_clip_above_default_replacement_is_empty(sample_rows):
    result = list(clip_above(iter(sample_rows), "score", threshold=50))
    assert result[3]["score"] == ""
