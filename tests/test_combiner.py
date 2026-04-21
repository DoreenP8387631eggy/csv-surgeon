"""Tests for csv_surgeon/combiner.py"""

import pytest
from csv_surgeon.combiner import combine_template, combine_columns, combine_with


@pytest.fixture
def sample_rows():
    return [
        {"first": "Alice", "last": "Smith", "city": "London"},
        {"first": "Bob", "last": "Jones", "city": ""},
        {"first": "", "last": "Taylor", "city": "Paris"},
    ]


def apply(fn, rows):
    return list(fn(rows))


def test_combine_template_adds_output_column(sample_rows):
    result = apply(lambda r: combine_template(r, "{first} {last}"), sample_rows)
    assert "combined" in result[0]


def test_combine_template_correct_value(sample_rows):
    result = apply(lambda r: combine_template(r, "{first} {last}"), sample_rows)
    assert result[0]["combined"] == "Alice Smith"


def test_combine_template_custom_output_col(sample_rows):
    result = apply(
        lambda r: combine_template(r, "{first}", output_col="name"), sample_rows
    )
    assert "name" in result[0]


def test_combine_template_missing_key_uses_default(sample_rows):
    result = apply(
        lambda r: combine_template(r, "{first} {missing}", default="N/A"), sample_rows
    )
    assert result[0]["combined"] == "Alice N/A"


def test_combine_template_preserves_original_fields(sample_rows):
    result = apply(lambda r: combine_template(r, "{first}"), sample_rows)
    assert result[0]["first"] == "Alice"
    assert result[0]["last"] == "Smith"


def test_combine_columns_joins_values(sample_rows):
    result = apply(
        lambda r: combine_columns(r, ["first", "last"]), sample_rows
    )
    assert result[0]["combined"] == "Alice Smith"


def test_combine_columns_custom_separator(sample_rows):
    result = apply(
        lambda r: combine_columns(r, ["first", "last"], separator="-"), sample_rows
    )
    assert result[0]["combined"] == "Alice-Smith"


def test_combine_columns_skips_empty_by_default(sample_rows):
    result = apply(
        lambda r: combine_columns(r, ["first", "city"]), sample_rows
    )
    # Bob has empty city
    assert result[1]["combined"] == "Bob"


def test_combine_columns_keep_empty(sample_rows):
    result = apply(
        lambda r: combine_columns(r, ["first", "city"], skip_empty=False), sample_rows
    )
    assert result[1]["combined"] == "Bob "


def test_combine_columns_custom_output_col(sample_rows):
    result = apply(
        lambda r: combine_columns(r, ["first", "last"], output_col="full_name"),
        sample_rows,
    )
    assert "full_name" in result[0]


def test_combine_with_applies_function(sample_rows):
    result = apply(
        lambda r: combine_with(r, ["first", "last"], fn=lambda v: "|".join(v)),
        sample_rows,
    )
    assert result[0]["combined"] == "Alice|Smith"


def test_combine_with_custom_output_col(sample_rows):
    result = apply(
        lambda r: combine_with(
            r, ["first"], fn=lambda v: v[0].upper(), output_col="upper_first"
        ),
        sample_rows,
    )
    assert result[0]["upper_first"] == "ALICE"
