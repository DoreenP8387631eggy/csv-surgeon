import pytest
from csv_surgeon.cropper import (
    lstrip_column, rstrip_column, strip_column, remove_prefix, remove_suffix
)


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "name": "  Alice  ", "code": "###hello###"},
        {"id": "2", "name": "  Bob", "code": "hello"},
        {"id": "3", "name": "Carol  ", "code": "###world"},
    ]


def apply(fn, rows):
    return list(fn(rows))


def test_strip_column_removes_whitespace(sample_rows):
    result = apply(lambda r: strip_column(r, "name"), sample_rows)
    assert result[0]["name"] == "Alice"
    assert result[1]["name"] == "Bob"
    assert result[2]["name"] == "Carol"


def test_lstrip_column_removes_leading_only(sample_rows):
    result = apply(lambda r: lstrip_column(r, "name"), sample_rows)
    assert result[0]["name"] == "Alice  "
    assert result[2]["name"] == "Carol  "


def test_rstrip_column_removes_trailing_only(sample_rows):
    result = apply(lambda r: rstrip_column(r, "name"), sample_rows)
    assert result[0]["name"] == "  Alice"
    assert result[1]["name"] == "  Bob"


def test_strip_column_with_custom_chars(sample_rows):
    result = apply(lambda r: strip_column(r, "code", "#"), sample_rows)
    assert result[0]["code"] == "hello"
    assert result[1]["code"] == "hello"
    assert result[2]["code"] == "world"


def test_lstrip_column_with_custom_chars(sample_rows):
    result = apply(lambda r: lstrip_column(r, "code", "#"), sample_rows)
    assert result[0]["code"] == "hello###"
    assert result[2]["code"] == "world"


def test_rstrip_column_with_custom_chars(sample_rows):
    result = apply(lambda r: rstrip_column(r, "code", "#"), sample_rows)
    assert result[0]["code"] == "###hello"


def test_remove_prefix_strips_matching(sample_rows):
    result = apply(lambda r: remove_prefix(r, "code", "###"), sample_rows)
    assert result[0]["code"] == "hello###"
    assert result[1]["code"] == "hello"


def test_remove_prefix_no_match_unchanged(sample_rows):
    result = apply(lambda r: remove_prefix(r, "code", "XXX"), sample_rows)
    assert result[0]["code"] == "###hello###"


def test_remove_suffix_strips_matching(sample_rows):
    result = apply(lambda r: remove_suffix(r, "code", "###"), sample_rows)
    assert result[0]["code"] == "###hello"
    assert result[2]["code"] == "###world"


def test_remove_suffix_no_match_unchanged(sample_rows):
    result = apply(lambda r: remove_suffix(r, "code", "ZZZ"), sample_rows)
    assert result[0]["code"] == "###hello###"


def test_missing_column_is_noop(sample_rows):
    result = apply(lambda r: strip_column(r, "nonexistent"), sample_rows)
    assert result[0] == sample_rows[0]


def test_does_not_mutate_original(sample_rows):
    original = [{**r} for r in sample_rows]
    list(strip_column(sample_rows, "name"))
    assert sample_rows[0]["name"] == original[0]["name"]


def test_preserves_other_fields(sample_rows):
    result = apply(lambda r: strip_column(r, "name"), sample_rows)
    assert result[0]["id"] == "1"
    assert result[0]["code"] == "###hello###"
