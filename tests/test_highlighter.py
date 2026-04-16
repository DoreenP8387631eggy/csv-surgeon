import pytest
from csv_surgeon.highlighter import (
    highlight_rows,
    highlight_equals,
    highlight_contains,
    highlight_numeric_range,
)


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "city": "London", "score": "85"},
        {"name": "Bob",   "city": "Paris",  "score": "42"},
        {"name": "Carol", "city": "london", "score": "67"},
    ]


def test_highlight_rows_adds_column(sample_rows):
    result = list(highlight_rows(sample_rows, lambda r: True))
    assert all("_highlight" in r for r in result)


def test_highlight_rows_true_value(sample_rows):
    result = list(highlight_rows(sample_rows, lambda r: True, true_value="yes"))
    assert all(r["_highlight"] == "yes" for r in result)


def test_highlight_rows_false_value(sample_rows):
    result = list(highlight_rows(sample_rows, lambda r: False, false_value="no"))
    assert all(r["_highlight"] == "no" for r in result)


def test_highlight_rows_preserves_original_fields(sample_rows):
    result = list(highlight_rows(sample_rows, lambda r: True))
    assert result[0]["name"] == "Alice"


def test_highlight_rows_custom_column_name(sample_rows):
    result = list(highlight_rows(sample_rows, lambda r: True, column="flagged"))
    assert "flagged" in result[0]
    assert "_highlight" not in result[0]


def test_highlight_equals_matches(sample_rows):
    result = list(highlight_equals(sample_rows, "city", "London"))
    assert result[0]["_highlight"] == "1"
    assert result[1]["_highlight"] == "0"


def test_highlight_equals_case_insensitive(sample_rows):
    result = list(highlight_equals(sample_rows, "city", "london", case_sensitive=False))
    assert result[0]["_highlight"] == "1"
    assert result[2]["_highlight"] == "1"


def test_highlight_equals_case_sensitive_no_match(sample_rows):
    result = list(highlight_equals(sample_rows, "city", "london", case_sensitive=True))
    assert result[0]["_highlight"] == "0"
    assert result[2]["_highlight"] == "1"


def test_highlight_contains_basic(sample_rows):
    result = list(highlight_contains(sample_rows, "city", "on"))
    assert result[0]["_highlight"] == "1"  # London
    assert result[1]["_highlight"] == "0"  # Paris


def test_highlight_contains_case_insensitive(sample_rows):
    result = list(highlight_contains(sample_rows, "city", "LON", case_sensitive=False))
    assert result[0]["_highlight"] == "1"
    assert result[2]["_highlight"] == "1"


def test_highlight_numeric_range_within(sample_rows):
    result = list(highlight_numeric_range(sample_rows, "score", 60, 90))
    assert result[0]["_highlight"] == "1"  # 85
    assert result[1]["_highlight"] == "0"  # 42
    assert result[2]["_highlight"] == "1"  # 67


def test_highlight_numeric_range_non_numeric_is_false():
    rows = [{"score": "n/a"}]
    result = list(highlight_numeric_range(rows, "score", 0, 100))
    assert result[0]["_highlight"] == "0"


def test_highlight_numeric_range_boundary_inclusive():
    rows = [{"v": "10"}, {"v": "20"}, {"v": "15"}]
    result = list(highlight_numeric_range(rows, "v", 10, 20))
    assert all(r["_highlight"] == "1" for r in result)
