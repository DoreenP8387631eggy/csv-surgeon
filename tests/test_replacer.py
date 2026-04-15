"""Tests for csv_surgeon.replacer."""

import pytest
from csv_surgeon.replacer import replace_value, replace_pattern, replace_map


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "status": "active", "code": "A1"},
        {"name": "Bob", "status": "inactive", "code": "B2"},
        {"name": "Charlie", "status": "active", "code": "A3"},
    ]


# --- replace_value ---

def test_replace_value_exact_match(sample_rows):
    transform = replace_value("status", "active", "enabled")
    result = list(transform(iter(sample_rows)))
    assert result[0]["status"] == "enabled"
    assert result[2]["status"] == "enabled"


def test_replace_value_no_match_unchanged(sample_rows):
    transform = replace_value("status", "pending", "waiting")
    result = list(transform(iter(sample_rows)))
    assert result[0]["status"] == "active"
    assert result[1]["status"] == "inactive"


def test_replace_value_case_insensitive(sample_rows):
    transform = replace_value("status", "ACTIVE", "enabled", case_sensitive=False)
    result = list(transform(iter(sample_rows)))
    assert result[0]["status"] == "enabled"
    assert result[2]["status"] == "enabled"


def test_replace_value_case_sensitive_no_match(sample_rows):
    transform = replace_value("status", "ACTIVE", "enabled", case_sensitive=True)
    result = list(transform(iter(sample_rows)))
    assert result[0]["status"] == "active"  # unchanged


def test_replace_value_missing_column_is_noop(sample_rows):
    transform = replace_value("nonexistent", "x", "y")
    result = list(transform(iter(sample_rows)))
    assert result[0] == sample_rows[0]


# --- replace_pattern ---

def test_replace_pattern_basic(sample_rows):
    transform = replace_pattern("code", r"[A-Z]", "X")
    result = list(transform(iter(sample_rows)))
    assert result[0]["code"] == "X1"
    assert result[1]["code"] == "X2"


def test_replace_pattern_removes_digits(sample_rows):
    transform = replace_pattern("code", r"\d", "")
    result = list(transform(iter(sample_rows)))
    assert result[0]["code"] == "A"
    assert result[1]["code"] == "B"


def test_replace_pattern_no_match_unchanged(sample_rows):
    transform = replace_pattern("name", r"\d+", "NUM")
    result = list(transform(iter(sample_rows)))
    assert result[0]["name"] == "Alice"


def test_replace_pattern_missing_column_is_noop(sample_rows):
    transform = replace_pattern("missing", r".", "X")
    result = list(transform(iter(sample_rows)))
    assert result[0] == sample_rows[0]


# --- replace_map ---

def test_replace_map_basic(sample_rows):
    mapping = {"active": "on", "inactive": "off"}
    transform = replace_map("status", mapping)
    result = list(transform(iter(sample_rows)))
    assert result[0]["status"] == "on"
    assert result[1]["status"] == "off"
    assert result[2]["status"] == "on"


def test_replace_map_unmapped_unchanged(sample_rows):
    mapping = {"active": "on"}
    transform = replace_map("status", mapping)
    result = list(transform(iter(sample_rows)))
    assert result[1]["status"] == "inactive"  # not in map, unchanged


def test_replace_map_default_used_for_unmapped(sample_rows):
    mapping = {"active": "on"}
    transform = replace_map("status", mapping, default="unknown")
    result = list(transform(iter(sample_rows)))
    assert result[1]["status"] == "unknown"


def test_replace_map_missing_column_is_noop(sample_rows):
    transform = replace_map("missing", {"a": "b"})
    result = list(transform(iter(sample_rows)))
    assert result[0] == sample_rows[0]
