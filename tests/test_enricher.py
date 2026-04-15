"""Tests for csv_surgeon.enricher."""

import pytest
from csv_surgeon.enricher import combine_columns, conditional_column, derive_column


@pytest.fixture
def sample_rows():
    return [
        {"first": "Jane", "last": "Doe", "score": "82"},
        {"first": "John", "last": "Smith", "score": "45"},
        {"first": "Alice", "last": "Wonder", "score": "99"},
    ]


def apply(transform, rows):
    return list(transform(rows))


# --- derive_column ---

def test_derive_column_adds_new_column(sample_rows):
    t = derive_column("full", lambda r: f"{r['first']} {r['last']}")
    result = apply(t, sample_rows)
    assert result[0]["full"] == "Jane Doe"
    assert result[1]["full"] == "John Smith"


def test_derive_column_does_not_overwrite_by_default(sample_rows):
    rows = [{"name": "existing", "x": "1"}]
    t = derive_column("name", lambda r: "new")
    result = apply(t, rows)
    assert result[0]["name"] == "existing"


def test_derive_column_overwrites_when_flag_set(sample_rows):
    rows = [{"name": "existing", "x": "1"}]
    t = derive_column("name", lambda r: "new", overwrite=True)
    result = apply(t, rows)
    assert result[0]["name"] == "new"


def test_derive_column_expression_error_yields_empty(sample_rows):
    t = derive_column("bad", lambda r: r["nonexistent"])
    result = apply(t, sample_rows)
    assert all(r["bad"] == "" for r in result)


def test_derive_column_preserves_existing_columns(sample_rows):
    t = derive_column("tag", lambda r: "ok")
    result = apply(t, sample_rows)
    assert result[0]["first"] == "Jane"
    assert result[0]["score"] == "82"


# --- combine_columns ---

def test_combine_columns_joins_with_separator(sample_rows):
    t = combine_columns("full_name", ["first", "last"], separator=" ")
    result = apply(t, sample_rows)
    assert result[0]["full_name"] == "Jane Doe"


def test_combine_columns_custom_separator(sample_rows):
    t = combine_columns("key", ["first", "last"], separator="_")
    result = apply(t, sample_rows)
    assert result[1]["key"] == "John_Smith"


def test_combine_columns_missing_source_treated_as_empty():
    rows = [{"a": "hello"}]
    t = combine_columns("out", ["a", "b"], separator="-")
    result = apply(t, rows)
    assert result[0]["out"] == "hello-"


def test_combine_columns_no_overwrite_by_default():
    rows = [{"full_name": "keep me", "first": "A", "last": "B"}]
    t = combine_columns("full_name", ["first", "last"])
    result = apply(t, rows)
    assert result[0]["full_name"] == "keep me"


# --- conditional_column ---

def test_conditional_column_true_branch(sample_rows):
    t = conditional_column("grade", lambda r: int(r["score"]) >= 50, "pass", "fail")
    result = apply(t, sample_rows)
    assert result[0]["grade"] == "pass"
    assert result[1]["grade"] == "fail"
    assert result[2]["grade"] == "pass"


def test_conditional_column_default_false_value(sample_rows):
    t = conditional_column("high", lambda r: int(r["score"]) > 90, "yes")
    result = apply(t, sample_rows)
    assert result[0]["high"] == ""
    assert result[2]["high"] == "yes"


def test_conditional_column_error_uses_false_value(sample_rows):
    t = conditional_column("x", lambda r: int(r["missing"]) > 0, "yes", "no")
    result = apply(t, sample_rows)
    assert all(r["x"] == "no" for r in result)


def test_conditional_column_no_overwrite_by_default():
    rows = [{"flag": "existing", "score": "10"}]
    t = conditional_column("flag", lambda r: True, "new")
    result = apply(t, rows)
    assert result[0]["flag"] == "existing"
