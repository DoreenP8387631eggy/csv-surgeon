"""Tests for csv_surgeon/converter.py"""
import pytest
from csv_surgeon.converter import (
    to_int,
    to_float,
    to_upper,
    to_lower,
    strip_whitespace,
    apply_conversions,
)


@pytest.fixture
def sample_row():
    return {"name": "  Alice  ", "age": "30.7", "score": "95", "city": "New York"}


def test_to_int_converts_float_string(sample_row):
    result = to_int("age")(dict(sample_row))
    assert result["age"] == "30"


def test_to_int_converts_integer_string(sample_row):
    result = to_int("score")(dict(sample_row))
    assert result["score"] == "95"


def test_to_int_non_numeric_becomes_empty(sample_row):
    result = to_int("name")(dict(sample_row))
    assert result["name"] == ""


def test_to_int_missing_column_is_noop(sample_row):
    result = to_int("nonexistent")(dict(sample_row))
    assert "nonexistent" not in result


def test_to_float_basic(sample_row):
    result = to_float("age")(dict(sample_row))
    assert result["age"] == "30.7"


def test_to_float_with_precision(sample_row):
    result = to_float("age", precision=2)(dict(sample_row))
    assert result["age"] == "30.70"


def test_to_float_non_numeric_becomes_empty(sample_row):
    result = to_float("city")(dict(sample_row))
    assert result["city"] == ""


def test_to_float_missing_column_is_noop(sample_row):
    result = to_float("missing")(dict(sample_row))
    assert "missing" not in result


def test_to_upper(sample_row):
    result = to_upper("city")(dict(sample_row))
    assert result["city"] == "NEW YORK"


def test_to_lower(sample_row):
    result = to_lower("city")(dict(sample_row))
    assert result["city"] == "new york"


def test_strip_whitespace(sample_row):
    result = strip_whitespace("name")(dict(sample_row))
    assert result["name"] == "Alice"


def test_strip_whitespace_missing_column_is_noop(sample_row):
    result = strip_whitespace("missing")(dict(sample_row))
    assert "missing" not in result


def test_apply_conversions_chains_transforms():
    rows = [
        {"name": "  bob  ", "age": "25.9"},
        {"name": "  carol  ", "age": "invalid"},
    ]
    transforms = [strip_whitespace("name"), to_upper("name"), to_int("age")]
    results = list(apply_conversions(iter(rows), transforms))
    assert results[0] == {"name": "BOB", "age": "25"}
    assert results[1] == {"name": "CAROL", "age": ""}


def test_apply_conversions_empty_transforms():
    rows = [{"a": "1"}]
    results = list(apply_conversions(iter(rows), []))
    assert results == [{"a": "1"}]


def test_apply_conversions_empty_rows():
    results = list(apply_conversions(iter([]), [to_upper("name")]))
    assert results == []
