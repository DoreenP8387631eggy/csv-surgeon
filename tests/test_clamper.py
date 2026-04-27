"""Tests for csv_surgeon.clamper."""
import pytest
from csv_surgeon.clamper import clamp_length_min, clamp_length_max, clamp_length


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "name": "Hi", "note": "short"},
        {"id": "2", "name": "Hello World", "note": "this is a longer note"},
        {"id": "3", "name": "", "note": ""},
    ]


def apply(fn, rows):
    return list(fn(iter(rows)))


# --- clamp_length_min ---

def test_clamp_min_pads_short_value(sample_rows):
    result = apply(lambda r: clamp_length_min(r, "name", 6), sample_rows)
    assert result[0]["name"] == "Hi    "


def test_clamp_min_leaves_long_value_unchanged(sample_rows):
    result = apply(lambda r: clamp_length_min(r, "name", 4), sample_rows)
    assert result[1]["name"] == "Hello World"


def test_clamp_min_pad_left(sample_rows):
    result = apply(lambda r: clamp_length_min(r, "name", 5, pad_right=False), sample_rows)
    assert result[0]["name"] == "   Hi"


def test_clamp_min_custom_pad_char(sample_rows):
    result = apply(lambda r: clamp_length_min(r, "name", 5, pad_char="0"), sample_rows)
    assert result[0]["name"] == "Hi000"


def test_clamp_min_empty_value_padded(sample_rows):
    result = apply(lambda r: clamp_length_min(r, "name", 3), sample_rows)
    assert result[2]["name"] == "   "


def test_clamp_min_missing_column_is_noop(sample_rows):
    result = apply(lambda r: clamp_length_min(r, "missing", 5), sample_rows)
    assert result[0] == sample_rows[0]


# --- clamp_length_max ---

def test_clamp_max_truncates_long_value(sample_rows):
    result = apply(lambda r: clamp_length_max(r, "note", 5), sample_rows)
    assert result[1]["note"] == "this "


def test_clamp_max_leaves_short_value_unchanged(sample_rows):
    result = apply(lambda r: clamp_length_max(r, "note", 10), sample_rows)
    assert result[0]["note"] == "short"


def test_clamp_max_with_suffix(sample_rows):
    result = apply(lambda r: clamp_length_max(r, "note", 8, suffix="..."), sample_rows)
    assert result[1]["note"] == "this ..."
    assert len(result[1]["note"]) == 8


def test_clamp_max_suffix_longer_than_max_uses_suffix(sample_rows):
    result = apply(lambda r: clamp_length_max(r, "note", 2, suffix="..."), sample_rows)
    # cut = 2 - 3 = -1, so suffix[:2] = '..' is used
    assert len(result[1]["note"]) <= 2


def test_clamp_max_missing_column_is_noop(sample_rows):
    result = apply(lambda r: clamp_length_max(r, "missing", 5), sample_rows)
    assert result[0] == sample_rows[0]


# --- clamp_length (combined) ---

def test_clamp_length_applies_both_bounds(sample_rows):
    result = apply(lambda r: clamp_length(r, "name", min_len=5, max_len=8), sample_rows)
    assert len(result[0]["name"]) == 5   # padded
    assert len(result[1]["name"]) == 8   # truncated


def test_clamp_length_no_bounds_is_passthrough(sample_rows):
    result = apply(lambda r: clamp_length(r, "name"), sample_rows)
    assert result[0]["name"] == sample_rows[0]["name"]


def test_clamp_length_preserves_other_columns(sample_rows):
    result = apply(lambda r: clamp_length(r, "name", max_len=3), sample_rows)
    assert result[0]["id"] == "1"
    assert result[0]["note"] == "short"
