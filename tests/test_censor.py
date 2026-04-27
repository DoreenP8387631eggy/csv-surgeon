"""Tests for csv_surgeon.censor."""
import pytest
from csv_surgeon.censor import (
    censor_column,
    censor_columns,
    censor_if,
    censor_pattern,
)


@pytest.fixture()
def sample_rows():
    return [
        {"name": "Alice", "email": "alice@example.com", "score": "95"},
        {"name": "Bob", "email": "bob@example.com", "score": "42"},
        {"name": "Carol", "email": "carol@example.com", "score": "78"},
    ]


def test_censor_column_replaces_all_values(sample_rows):
    result = list(censor_column(sample_rows, "email"))
    assert all(r["email"] == "***" for r in result)


def test_censor_column_custom_replacement(sample_rows):
    result = list(censor_column(sample_rows, "name", replacement="[REDACTED]"))
    assert result[0]["name"] == "[REDACTED]"


def test_censor_column_preserves_other_fields(sample_rows):
    result = list(censor_column(sample_rows, "email"))
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == "95"


def test_censor_column_missing_column_is_noop(sample_rows):
    result = list(censor_column(sample_rows, "nonexistent"))
    assert result[0] == sample_rows[0]


def test_censor_pattern_replaces_matching_substring(sample_rows):
    result = list(censor_pattern(sample_rows, "email", r"@.*"))
    assert result[0]["email"] == "alice***"


def test_censor_pattern_no_match_leaves_value_unchanged(sample_rows):
    result = list(censor_pattern(sample_rows, "name", r"\d+"))
    assert result[0]["name"] == "Alice"


def test_censor_pattern_custom_replacement(sample_rows):
    result = list(censor_pattern(sample_rows, "email", r"@[^.]+", replacement="@***"))
    assert "@***" in result[0]["email"]


def test_censor_columns_redacts_multiple_cols(sample_rows):
    result = list(censor_columns(sample_rows, ["name", "email"]))
    assert result[0]["name"] == "***"
    assert result[0]["email"] == "***"


def test_censor_columns_preserves_unlisted_col(sample_rows):
    result = list(censor_columns(sample_rows, ["name", "email"]))
    assert result[0]["score"] == "95"


def test_censor_columns_ignores_missing_cols(sample_rows):
    result = list(censor_columns(sample_rows, ["ghost", "email"]))
    assert result[0]["email"] == "***"


def test_censor_if_redacts_when_predicate_true(sample_rows):
    result = list(censor_if(sample_rows, "score", lambda v: int(v) < 50))
    assert result[1]["score"] == "***"  # Bob score 42
    assert result[0]["score"] == "95"  # Alice untouched


def test_censor_if_preserves_other_fields(sample_rows):
    result = list(censor_if(sample_rows, "score", lambda v: int(v) < 50))
    assert result[1]["name"] == "Bob"


def test_censor_does_not_mutate_original(sample_rows):
    original_email = sample_rows[0]["email"]
    list(censor_column(sample_rows, "email"))
    assert sample_rows[0]["email"] == original_email
