import pytest
from csv_surgeon.coalescer import coalesce_columns, coalesce_fill, first_valid


@pytest.fixture
def sample_rows():
    return [
        {"a": "", "b": "", "c": "hello"},
        {"a": "first", "b": "second", "c": "third"},
        {"a": "", "b": "beta", "c": "gamma"},
        {"a": "  ", "b": "", "c": ""},
    ]


def test_coalesce_columns_picks_first_non_empty(sample_rows):
    result = list(coalesce_columns(iter(sample_rows), ["a", "b", "c"], "out"))
    assert result[0]["out"] == "hello"


def test_coalesce_columns_picks_first_when_all_present(sample_rows):
    result = list(coalesce_columns(iter(sample_rows), ["a", "b", "c"], "out"))
    assert result[1]["out"] == "first"


def test_coalesce_columns_skips_empty_picks_second(sample_rows):
    result = list(coalesce_columns(iter(sample_rows), ["a", "b", "c"], "out"))
    assert result[2]["out"] == "beta"


def test_coalesce_columns_default_when_all_empty(sample_rows):
    result = list(coalesce_columns(iter(sample_rows), ["a", "b", "c"], "out", default="N/A"))
    assert result[3]["out"] == "N/A"


def test_coalesce_columns_preserves_original_fields(sample_rows):
    result = list(coalesce_columns(iter(sample_rows), ["a", "b", "c"], "out"))
    assert result[0]["a"] == ""
    assert result[0]["c"] == "hello"


def test_coalesce_columns_adds_new_output_column(sample_rows):
    result = list(coalesce_columns(iter(sample_rows), ["a", "b"], "chosen"))
    assert "chosen" in result[0]


def test_coalesce_fill_replaces_empty_with_fallback():
    rows = [{"name": "", "alias": "Neo", "id": "1"}]
    result = list(coalesce_fill(iter(rows), "name", ["alias"]))
    assert result[0]["name"] == "Neo"


def test_coalesce_fill_keeps_existing_value():
    rows = [{"name": "Thomas", "alias": "Neo"}]
    result = list(coalesce_fill(iter(rows), "name", ["alias"]))
    assert result[0]["name"] == "Thomas"


def test_coalesce_fill_tries_fallbacks_in_order():
    rows = [{"name": "", "alias": "", "nickname": "Neo"}]
    result = list(coalesce_fill(iter(rows), "name", ["alias", "nickname"]))
    assert result[0]["name"] == "Neo"


def test_first_valid_uses_predicate():
    rows = [{"x": "0", "y": "5", "z": "3"}]
    result = list(first_valid(iter(rows), ["x", "y", "z"], "out", predicate=lambda v: v.strip() not in ("", "0")))
    assert result[0]["out"] == "5"


def test_first_valid_empty_when_none_match():
    rows = [{"x": "0", "y": "0"}]
    result = list(first_valid(iter(rows), ["x", "y"], "out", predicate=lambda v: v == "1"))
    assert result[0]["out"] == ""
