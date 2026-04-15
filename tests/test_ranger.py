"""Tests for csv_surgeon.ranger."""

import pytest
from csv_surgeon.ranger import slice_rows, skip_rows, limit_rows, rows_between


@pytest.fixture
def sample_rows():
    return [
        {"id": str(i), "val": f"v{i}"}
        for i in range(10)
    ]


# --- slice_rows ---

def test_slice_rows_full_range(sample_rows):
    result = list(slice_rows(sample_rows))
    assert result == sample_rows


def test_slice_rows_with_start(sample_rows):
    result = list(slice_rows(sample_rows, start=3))
    assert result[0]["id"] == "3"
    assert len(result) == 7


def test_slice_rows_with_stop(sample_rows):
    result = list(slice_rows(sample_rows, stop=4))
    assert len(result) == 4
    assert result[-1]["id"] == "3"


def test_slice_rows_with_step(sample_rows):
    result = list(slice_rows(sample_rows, step=2))
    assert [r["id"] for r in result] == ["0", "2", "4", "6", "8"]


def test_slice_rows_start_stop_step(sample_rows):
    result = list(slice_rows(sample_rows, start=1, stop=8, step=3))
    assert [r["id"] for r in result] == ["1", "4", "7"]


def test_slice_rows_invalid_step(sample_rows):
    with pytest.raises(ValueError, match="step"):
        list(slice_rows(sample_rows, step=0))


# --- skip_rows ---

def test_skip_rows_skips_correct_count(sample_rows):
    result = list(skip_rows(sample_rows, 3))
    assert len(result) == 7
    assert result[0]["id"] == "3"


def test_skip_rows_zero_skips_nothing(sample_rows):
    result = list(skip_rows(sample_rows, 0))
    assert result == sample_rows


def test_skip_rows_more_than_length(sample_rows):
    result = list(skip_rows(sample_rows, 100))
    assert result == []


def test_skip_rows_negative_raises(sample_rows):
    with pytest.raises(ValueError):
        list(skip_rows(sample_rows, -1))


# --- limit_rows ---

def test_limit_rows_returns_correct_count(sample_rows):
    result = list(limit_rows(sample_rows, 4))
    assert len(result) == 4
    assert result[-1]["id"] == "3"


def test_limit_rows_larger_than_input(sample_rows):
    result = list(limit_rows(sample_rows, 50))
    assert result == sample_rows


def test_limit_rows_zero_returns_empty(sample_rows):
    result = list(limit_rows(sample_rows, 0))
    assert result == []


def test_limit_rows_negative_raises(sample_rows):
    with pytest.raises(ValueError):
        list(limit_rows(sample_rows, -1))


# --- rows_between ---

def test_rows_between_basic(sample_rows):
    result = list(rows_between(sample_rows, 2, 5))
    assert [r["id"] for r in result] == ["2", "3", "4"]


def test_rows_between_stop_equals_start_returns_empty(sample_rows):
    result = list(rows_between(sample_rows, 3, 3))
    assert result == []


def test_rows_between_stop_less_than_start_returns_empty(sample_rows):
    result = list(rows_between(sample_rows, 5, 2))
    assert result == []


def test_rows_between_negative_raises(sample_rows):
    with pytest.raises(ValueError):
        list(rows_between(sample_rows, -1, 5))
