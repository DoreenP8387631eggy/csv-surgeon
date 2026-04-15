"""Tests for csv_surgeon.aggregator module."""

import pytest
from csv_surgeon.aggregator import (
    count,
    sum_column,
    min_column,
    max_column,
    average_column,
    value_counts,
)


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "score": "90", "grade": "A"},
        {"name": "Bob", "score": "75", "grade": "B"},
        {"name": "Carol", "score": "85", "grade": "A"},
        {"name": "Dave", "score": "", "grade": "B"},
        {"name": "Eve", "score": "95", "grade": "A"},
    ]


def test_count_all_rows(sample_rows):
    assert count(sample_rows) == 5


def test_count_with_column_skips_empty(sample_rows):
    assert count(sample_rows, column="score") == 4


def test_sum_column(sample_rows):
    assert sum_column(sample_rows, "score") == pytest.approx(345.0)


def test_sum_column_skips_non_numeric(sample_rows):
    # 'grade' column has no numeric values
    assert sum_column(sample_rows, "grade") == 0.0


def test_min_column(sample_rows):
    assert min_column(sample_rows, "score") == pytest.approx(75.0)


def test_min_column_all_non_numeric():
    rows = [{"val": "abc"}, {"val": "def"}]
    assert min_column(rows, "val") is None


def test_max_column(sample_rows):
    assert max_column(sample_rows, "score") == pytest.approx(95.0)


def test_max_column_empty_input():
    assert max_column([], "score") is None


def test_average_column(sample_rows):
    # 90 + 75 + 85 + 95 = 345, count = 4
    assert average_column(sample_rows, "score") == pytest.approx(86.25)


def test_average_column_no_valid_values():
    rows = [{"val": "x"}, {"val": "y"}]
    assert average_column(rows, "val") is None


def test_value_counts(sample_rows):
    result = value_counts(sample_rows, "grade")
    assert result == {"A": 3, "B": 2}


def test_value_counts_empty_input():
    assert value_counts([], "grade") == {}


def test_value_counts_includes_empty_string():
    rows = [{"val": "x"}, {"val": ""}, {"val": "x"}]
    result = value_counts(rows, "val")
    assert result["x"] == 2
    assert result[""] == 1
