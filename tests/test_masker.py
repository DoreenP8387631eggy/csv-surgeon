"""Tests for csv_surgeon.masker."""

import pytest
from csv_surgeon.masker import mask_column, redact_column, mask_pattern


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "email": "alice@example.com", "card": "1234567890123456"},
        {"name": "Bob",   "email": "bob@test.org",      "card": "9876543210987654"},
        {"name": "",      "email": "",                  "card": ""},
    ]


def apply(transform, rows):
    return list(transform(iter(rows)))


# --- mask_column ---

def test_mask_column_replaces_all_chars(sample_rows):
    result = apply(mask_column("name"), sample_rows)
    assert result[0]["name"] == "*****"
    assert result[1]["name"] == "***"


def test_mask_column_keeps_last_chars(sample_rows):
    result = apply(mask_column("card", keep_last=4), sample_rows)
    assert result[0]["card"] == "************3456"
    assert result[1]["card"] == "************7654"


def test_mask_column_empty_value_unchanged(sample_rows):
    result = apply(mask_column("email"), sample_rows)
    assert result[2]["email"] == ""


def test_mask_column_missing_column_is_noop(sample_rows):
    result = apply(mask_column("phone"), sample_rows)
    assert "phone" not in result[0]
    assert result[0]["name"] == "Alice"


def test_mask_column_custom_char(sample_rows):
    result = apply(mask_column("name", mask_char="X"), sample_rows)
    assert result[0]["name"] == "XXXXX"


def test_mask_column_keep_last_larger_than_value():
    rows = [{"pin": "123"}]
    result = apply(mask_column("pin", keep_last=10), rows)
    # keep_last >= len(value) → full mask
    assert result[0]["pin"] == "***"


# --- redact_column ---

def test_redact_column_replaces_value(sample_rows):
    result = apply(redact_column("email"), sample_rows)
    assert result[0]["email"] == "[REDACTED]"
    assert result[1]["email"] == "[REDACTED]"


def test_redact_column_custom_replacement(sample_rows):
    result = apply(redact_column("name", replacement="HIDDEN"), sample_rows)
    assert result[0]["name"] == "HIDDEN"


def test_redact_column_missing_column_is_noop(sample_rows):
    result = apply(redact_column("ssn"), sample_rows)
    assert "ssn" not in result[0]


# --- mask_pattern ---

def test_mask_pattern_replaces_matching_substring():
    rows = [{"note": "Call 555-1234 for info"}]
    result = apply(mask_pattern("note", r"\d{3}-\d{4}"), rows)
    assert result[0]["note"] == "Call ******** for info"


def test_mask_pattern_multiple_matches():
    rows = [{"text": "SSN: 123-45-6789 and 987-65-4321"}]
    result = apply(mask_pattern("text", r"\d{3}-\d{2}-\d{4}"), rows)
    assert result[0]["text"] == "SSN: *********** and ***********"


def test_mask_pattern_no_match_unchanged():
    rows = [{"text": "no digits here"}]
    result = apply(mask_pattern("text", r"\d+"), rows)
    assert result[0]["text"] == "no digits here"


def test_mask_pattern_missing_column_is_noop():
    rows = [{"name": "Alice"}]
    result = apply(mask_pattern("email", r"\S+@\S+"), rows)
    assert "email" not in result[0]
