"""Tests for csv_surgeon.flattener."""
import pytest
from csv_surgeon.flattener import flatten_column, flatten_prefix


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "name": "Alice", "tags": "python|data|csv"},
        {"id": "2", "name": "Bob",   "tags": "java"},
        {"id": "3", "name": "Carol", "tags": ""},
        {"id": "4", "name": "Dave",  "tags": "go | rust | c"},
    ]


# ---------------------------------------------------------------------------
# flatten_column
# ---------------------------------------------------------------------------

def test_flatten_column_expands_multiple_values(sample_rows):
    result = list(flatten_column(iter(sample_rows), "tags"))
    alice_tags = [r["tags"] for r in result if r["name"] == "Alice"]
    assert alice_tags == ["python", "data", "csv"]


def test_flatten_column_single_value_unchanged(sample_rows):
    result = list(flatten_column(iter(sample_rows), "tags"))
    bob_rows = [r for r in result if r["name"] == "Bob"]
    assert len(bob_rows) == 1
    assert bob_rows[0]["tags"] == "java"


def test_flatten_column_empty_value_passes_through(sample_rows):
    result = list(flatten_column(iter(sample_rows), "tags"))
    carol_rows = [r for r in result if r["name"] == "Carol"]
    assert len(carol_rows) == 1
    assert carol_rows[0]["tags"] == ""


def test_flatten_column_strips_whitespace(sample_rows):
    result = list(flatten_column(iter(sample_rows), "tags", strip=True))
    dave_tags = [r["tags"] for r in result if r["name"] == "Dave"]
    assert dave_tags == ["go", "rust", "c"]


def test_flatten_column_no_strip_preserves_spaces(sample_rows):
    result = list(flatten_column(iter(sample_rows), "tags", strip=False))
    dave_tags = [r["tags"] for r in result if r["name"] == "Dave"]
    assert dave_tags == ["go ", " rust ", " c"]


def test_flatten_column_preserves_other_fields(sample_rows):
    result = list(flatten_column(iter(sample_rows), "tags"))
    for r in result:
        assert "id" in r
        assert "name" in r


def test_flatten_column_missing_column_passes_through():
    rows = [{"id": "1", "name": "Alice"}]
    result = list(flatten_column(iter(rows), "tags"))
    assert result == [{"id": "1", "name": "Alice"}]


def test_flatten_column_custom_delimiter():
    rows = [{"id": "1", "vals": "a,b,c"}]
    result = list(flatten_column(iter(rows), "vals", delimiter=","))
    assert [r["vals"] for r in result] == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# flatten_prefix
# ---------------------------------------------------------------------------

@pytest.fixture
def prefixed_rows():
    return [
        {"id": "1", "addr_city": "London",   "addr_zip": "EC1",  "name": "Alice"},
        {"id": "2", "addr_city": "New York",  "addr_zip": "10001", "name": "Bob"},
    ]


def test_flatten_prefix_renames_matching_columns(prefixed_rows):
    result = list(flatten_prefix(iter(prefixed_rows), "addr"))
    assert "city" in result[0]
    assert "zip" in result[0]


def test_flatten_prefix_removes_original_by_default(prefixed_rows):
    result = list(flatten_prefix(iter(prefixed_rows), "addr"))
    assert "addr_city" not in result[0]
    assert "addr_zip" not in result[0]


def test_flatten_prefix_keep_original(prefixed_rows):
    result = list(flatten_prefix(iter(prefixed_rows), "addr", keep_original=True))
    assert "city" in result[0]
    assert "addr_city" in result[0]


def test_flatten_prefix_preserves_non_matching_columns(prefixed_rows):
    result = list(flatten_prefix(iter(prefixed_rows), "addr"))
    assert result[0]["id"] == "1"
    assert result[0]["name"] == "Alice"


def test_flatten_prefix_values_unchanged(prefixed_rows):
    result = list(flatten_prefix(iter(prefixed_rows), "addr"))
    assert result[0]["city"] == "London"
    assert result[1]["zip"] == "10001"
