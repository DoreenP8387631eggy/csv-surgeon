"""Tests for csv_surgeon.caster."""

import pytest
from csv_surgeon.caster import cast_column, cast_columns


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "age": "30", "score": "9.5", "active": "true"},
        {"name": "Bob",   "age": "25", "score": "7.0", "active": "false"},
        {"name": "Carol", "age": "40", "score": "8.25", "active": "1"},
    ]


def apply(transform, rows):
    return list(transform(iter(rows)))


# --- cast_column ---

def test_cast_column_to_int(sample_rows):
    result = apply(cast_column("age", "int"), sample_rows)
    assert result[0]["age"] == 30
    assert isinstance(result[0]["age"], int)


def test_cast_column_to_float(sample_rows):
    result = apply(cast_column("score", "float"), sample_rows)
    assert result[1]["score"] == pytest.approx(7.0)
    assert isinstance(result[1]["score"], float)


def test_cast_column_to_bool_true(sample_rows):
    result = apply(cast_column("active", "bool"), sample_rows)
    assert result[0]["active"] is True
    assert result[1]["active"] is False
    assert result[2]["active"] is True


def test_cast_column_to_str_unchanged(sample_rows):
    result = apply(cast_column("name", "str"), sample_rows)
    assert result[0]["name"] == "Alice"


def test_cast_column_invalid_value_preserved():
    rows = [{"age": "not_a_number"}]
    result = apply(cast_column("age", "int"), rows)
    # original value preserved on failure
    assert result[0]["age"] == "not_a_number"


def test_cast_column_missing_column_is_noop(sample_rows):
    result = apply(cast_column("missing", "int"), sample_rows)
    assert result == sample_rows


def test_cast_column_unsupported_type_raises():
    with pytest.raises(ValueError, match="Unsupported cast type"):
        cast_column("age", "datetime")


def test_cast_column_does_not_mutate_original(sample_rows):
    original_age = sample_rows[0]["age"]
    apply(cast_column("age", "int"), sample_rows)
    assert sample_rows[0]["age"] == original_age


# --- cast_columns ---

def test_cast_columns_multiple(sample_rows):
    result = apply(cast_columns({"age": "int", "score": "float"}), sample_rows)
    assert isinstance(result[0]["age"], int)
    assert isinstance(result[0]["score"], float)
    assert result[0]["name"] == "Alice"  # untouched


def test_cast_columns_empty_mapping_is_noop(sample_rows):
    result = apply(cast_columns({}), sample_rows)
    assert result == sample_rows


def test_cast_columns_float_string_to_int(sample_rows):
    # "9.5" -> int via float intermediate
    result = apply(cast_columns({"score": "int"}), sample_rows)
    assert result[0]["score"] == 9
