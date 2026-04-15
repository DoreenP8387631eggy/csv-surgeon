"""Tests for csv_surgeon.truncator."""

import pytest
from csv_surgeon.truncator import truncate_column, pad_column


@pytest.fixture()
def sample_rows():
    return [
        {"name": "Alexander", "city": "New York"},
        {"name": "Jo", "city": "LA"},
        {"name": "Bartholomew", "city": "San Francisco"},
    ]


# --- truncate_column ---

def test_truncate_shortens_long_values(sample_rows):
    transform = truncate_column("name", max_length=5)
    result = list(transform(iter(sample_rows)))
    assert result[0]["name"] == "Alexa"
    assert result[2]["name"] == "Barth"


def test_truncate_leaves_short_values_unchanged(sample_rows):
    transform = truncate_column("name", max_length=5)
    result = list(transform(iter(sample_rows)))
    assert result[1]["name"] == "Jo"


def test_truncate_with_suffix(sample_rows):
    transform = truncate_column("name", max_length=6, suffix="...")
    result = list(transform(iter(sample_rows)))
    # effective = 3 chars + "..."
    assert result[0]["name"] == "Ale..."
    assert len(result[0]["name"]) == 6


def test_truncate_suffix_exactly_fits():
    rows = [{"col": "hello"}]
    transform = truncate_column("col", max_length=5, suffix="!")
    result = list(transform(iter(rows)))
    assert result[0]["col"] == "hell!"


def test_truncate_missing_column_is_noop(sample_rows):
    transform = truncate_column("nonexistent", max_length=3)
    result = list(transform(iter(sample_rows)))
    assert result == sample_rows


def test_truncate_other_columns_unchanged(sample_rows):
    transform = truncate_column("name", max_length=4)
    result = list(transform(iter(sample_rows)))
    assert result[0]["city"] == "New York"


def test_truncate_suffix_longer_than_max_raises():
    with pytest.raises(ValueError):
        truncate_column("col", max_length=2, suffix="...")


# --- pad_column ---

def test_pad_left_pads_short_values():
    rows = [{"code": "A"}, {"code": "BC"}]
    transform = pad_column("code", width=4)
    result = list(transform(iter(rows)))
    assert result[0]["code"] == "A   "
    assert result[1]["code"] == "BC  "


def test_pad_right_alignment():
    rows = [{"code": "A"}]
    transform = pad_column("code", width=4, align="right")
    result = list(transform(iter(rows)))
    assert result[0]["code"] == "   A"


def test_pad_center_alignment():
    rows = [{"code": "A"}]
    transform = pad_column("code", width=5, align="center")
    result = list(transform(iter(rows)))
    assert result[0]["code"] == "  A  "


def test_pad_custom_fill_char():
    rows = [{"num": "7"}]
    transform = pad_column("num", width=4, fill_char="0", align="right")
    result = list(transform(iter(rows)))
    assert result[0]["num"] == "0007"


def test_pad_longer_than_width_unchanged():
    rows = [{"name": "Alexander"}]
    transform = pad_column("name", width=4)
    result = list(transform(iter(rows)))
    assert result[0]["name"] == "Alexander"


def test_pad_missing_column_is_noop():
    rows = [{"a": "x"}]
    transform = pad_column("z", width=5)
    result = list(transform(iter(rows)))
    assert result == rows


def test_pad_invalid_align_raises():
    with pytest.raises(ValueError):
        pad_column("col", width=5, align="diagonal")


def test_pad_invalid_fill_char_raises():
    with pytest.raises(ValueError):
        pad_column("col", width=5, fill_char="ab")
