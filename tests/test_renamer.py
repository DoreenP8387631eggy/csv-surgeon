"""Tests for csv_surgeon.renamer module."""

import pytest
from csv_surgeon.renamer import rename_columns, prefix_columns, suffix_columns


@pytest.fixture
def sample_rows():
    return [
        {"first_name": "Alice", "last_name": "Smith", "age": "30"},
        {"first_name": "Bob", "last_name": "Jones", "age": "25"},
        {"first_name": "Carol", "last_name": "White", "age": "40"},
    ]


def test_rename_columns_basic(sample_rows):
    mapping = {"first_name": "given_name", "last_name": "surname"}
    result = list(rename_columns(iter(sample_rows), mapping))
    assert result[0] == {"given_name": "Alice", "surname": "Smith", "age": "30"}


def test_rename_columns_preserves_values(sample_rows):
    mapping = {"age": "years"}
    result = list(rename_columns(iter(sample_rows), mapping))
    assert all(row["years"] == orig["age"] for row, orig in zip(result, sample_rows))


def test_rename_columns_missing_key_is_ignored(sample_rows):
    mapping = {"nonexistent": "something"}
    result = list(rename_columns(iter(sample_rows), mapping))
    assert result[0] == sample_rows[0]


def test_rename_columns_empty_mapping(sample_rows):
    result = list(rename_columns(iter(sample_rows), {}))
    assert result == sample_rows


def test_rename_columns_empty_rows():
    result = list(rename_columns(iter([]), {"a": "b"}))
    assert result == []


def test_rename_columns_old_key_removed(sample_rows):
    """Ensure the original key is not present after renaming."""
    mapping = {"first_name": "given_name"}
    result = list(rename_columns(iter(sample_rows), mapping))
    assert "first_name" not in result[0]


def test_rename_columns_all_rows_renamed(sample_rows):
    """Ensure renaming applies to every row, not just the first."""
    mapping = {"first_name": "given_name"}
    result = list(rename_columns(iter(sample_rows), mapping))
    assert all("given_name" in row and "first_name" not in row for row in result)


def test_prefix_columns_adds_prefix(sample_rows):
    result = list(prefix_columns(iter(sample_rows), "col_"))
    assert "col_first_name" in result[0]
    assert "col_last_name" in result[0]
    assert "col_age" in result[0]


def test_prefix_columns_preserves_values(sample_rows):
    result = list(prefix_columns(iter(sample_rows), "x_"))
    assert result[0]["x_first_name"] == "Alice"


def test_prefix_columns_exclude(sample_rows):
    result = list(prefix_columns(iter(sample_rows), "x_", exclude=["age"]))
    assert "age" in result[0]
    assert "x_age" not in result[0]
    assert "x_first_name" in result[0]


def test_prefix_columns_empty_prefix(sample_rows):
    result = list(prefix_columns(iter(sample_rows), ""))
    assert result == sample_rows


def test_suffix_columns_adds_suffix(sample_rows):
    result = list(suffix_columns(iter(sample_rows), "_col"))
    assert "first_name_col" in result[0]
    assert "last_name_col" in result[0]
    assert "age_col" in result[0]


def test_suffix_columns_preserves_values(sample_rows):
    result = list(suffix_columns(iter(sample_rows), "_s"))
    assert result[1]["first_name_s"] == "Bob"


def test_suffix_columns_exclude(sample_rows):
    result = list(suffix_columns(iter(sample_rows), "_s", exclude=["first_name"]))
    assert "first_name" in result[0]
    assert "first_name_s" not in result[0]
    assert "last_name_s" in result[0]


def test_suffix_columns_empty_rows():
    result = list(suffix_columns(iter([]), "_s"))
    assert result == []
