"""Tests for csv_surgeon.normalizer."""

import pytest
from csv_surgeon.normalizer import (
    strip_whitespace,
    normalize_whitespace,
    to_lowercase,
    to_titlecase,
    remove_non_alphanumeric,
    fill_empty,
)


def apply(transform, rows):
    return list(transform(iter(rows)))


@pytest.fixture
def sample_rows():
    return [
        {"name": "  Alice  ", "city": "New   York", "code": "A1-B2!"},
        {"name": "BOB", "city": "los angeles", "code": ""},
        {"name": "  charlie brown  ", "city": "  ", "code": "XY99"},
    ]


def test_strip_whitespace_removes_padding(sample_rows):
    result = apply(strip_whitespace("name"), sample_rows)
    assert result[0]["name"] == "Alice"
    assert result[2]["name"] == "charlie brown"


def test_strip_whitespace_missing_column_is_noop(sample_rows):
    result = apply(strip_whitespace("nonexistent"), sample_rows)
    assert result[0]["name"] == "  Alice  "


def test_normalize_whitespace_collapses_internal_spaces(sample_rows):
    result = apply(normalize_whitespace("city"), sample_rows)
    assert result[0]["city"] == "New York"


def test_normalize_whitespace_strips_ends(sample_rows):
    result = apply(normalize_whitespace("name"), sample_rows)
    assert result[2]["name"] == "charlie brown"


def test_to_lowercase_converts_value(sample_rows):
    result = apply(to_lowercase("name"), sample_rows)
    assert result[1]["name"] == "bob"


def test_to_lowercase_missing_column_is_noop(sample_rows):
    result = apply(to_lowercase("missing"), sample_rows)
    assert result[0]["name"] == "  Alice  "


def test_to_titlecase_converts_value(sample_rows):
    result = apply(to_titlecase("city"), sample_rows)
    assert result[1]["city"] == "Los Angeles"


def test_remove_non_alphanumeric_strips_symbols(sample_rows):
    result = apply(remove_non_alphanumeric("code"), sample_rows)
    assert result[0]["code"] == "A1B2"


def test_remove_non_alphanumeric_keep_spaces():
    rows = [{"desc": "hello world! 42"}]
    result = apply(remove_non_alphanumeric("desc", keep_spaces=True), rows)
    assert result[0]["desc"] == "hello world 42"


def test_remove_non_alphanumeric_empty_value_stays_empty(sample_rows):
    result = apply(remove_non_alphanumeric("code"), sample_rows)
    assert result[1]["code"] == ""


def test_fill_empty_replaces_empty_string():
    rows = [{"val": ""}, {"val": "hello"}, {"val": "  "}]
    result = apply(fill_empty("val", default="N/A"), rows)
    assert result[0]["val"] == "N/A"
    assert result[1]["val"] == "hello"
    assert result[2]["val"] == "N/A"


def test_fill_empty_default_is_empty_string():
    rows = [{"val": ""}]
    result = apply(fill_empty("val"), rows)
    assert result[0]["val"] == ""


def test_fill_empty_missing_column_is_noop():
    rows = [{"val": "data"}]
    result = apply(fill_empty("other", default="X"), rows)
    assert result[0]["val"] == "data"
