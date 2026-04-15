"""Tests for csv_surgeon.validator."""

import pytest
from csv_surgeon.validator import (
    required,
    is_numeric,
    max_length,
    one_of,
    validate_rows,
)


@pytest.fixture()
def sample_rows():
    return [
        {"name": "Alice", "age": "30", "role": "admin"},
        {"name": "Bob", "age": "not-a-number", "role": "user"},
        {"name": "", "age": "25", "role": "superadmin"},
        {"name": "Diana", "age": "28", "role": "user"},
    ]


# --- required ---

def test_required_passes_non_empty():
    ok, msg = required("name")({"name": "Alice"})
    assert ok is True
    assert msg == ""


def test_required_fails_empty_string():
    ok, msg = required("name")({"name": ""})
    assert ok is False
    assert "required" in msg


def test_required_fails_whitespace_only():
    ok, msg = required("name")({"name": "   "})
    assert ok is False


def test_required_fails_missing_column():
    ok, msg = required("email")({"name": "Alice"})
    assert ok is False


# --- is_numeric ---

def test_is_numeric_passes_integer_string():
    ok, _ = is_numeric("age")({"age": "42"})
    assert ok is True


def test_is_numeric_passes_float_string():
    ok, _ = is_numeric("score")({"score": "3.14"})
    assert ok is True


def test_is_numeric_fails_alpha():
    ok, msg = is_numeric("age")({"age": "old"})
    assert ok is False
    assert "not numeric" in msg


# --- max_length ---

def test_max_length_passes_within_limit():
    ok, _ = max_length("name", 10)({"name": "Alice"})
    assert ok is True


def test_max_length_fails_exceeds_limit():
    ok, msg = max_length("name", 3)({"name": "Alice"})
    assert ok is False
    assert "max length" in msg


# --- one_of ---

def test_one_of_passes_valid_choice():
    ok, _ = one_of("role", ["admin", "user"])({"role": "admin"})
    assert ok is True


def test_one_of_fails_invalid_choice():
    ok, msg = one_of("role", ["admin", "user"])({"role": "superadmin"})
    assert ok is False
    assert "not in" in msg


# --- validate_rows ---

def test_validate_rows_yields_all_rows(sample_rows):
    results = list(validate_rows(sample_rows, [required("name")]))
    assert len(results) == len(sample_rows)


def test_validate_rows_reports_errors(sample_rows):
    results = dict(
        (r["name"], errors)
        for r, errors in validate_rows(sample_rows, [required("name")])
    )
    # Row with empty name should have errors
    assert any(errors for errors in results.values())


def test_validate_rows_fail_fast_stops_early(sample_rows):
    validators = [required("name"), is_numeric("age")]
    for row, errors in validate_rows(sample_rows, validators, fail_fast=True):
        assert len(errors) <= 1


def test_validate_rows_multiple_validators_accumulate_errors():
    rows = [{"name": "", "age": "abc", "role": "god"}]
    validators = [required("name"), is_numeric("age"), one_of("role", ["admin"])]
    results = list(validate_rows(rows, validators))
    _, errors = results[0]
    assert len(errors) == 3
