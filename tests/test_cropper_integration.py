"""Integration tests chaining multiple cropper operations."""
from csv_surgeon.cropper import (
    strip_column, remove_prefix, remove_suffix, lstrip_column, rstrip_column
)


def _make_rows():
    return [
        {"id": "1", "tag": "  [hello]  "},
        {"id": "2", "tag": "  [world]  "},
        {"id": "3", "tag": "  []  "},
    ]


def test_strip_then_remove_prefix_and_suffix():
    rows = _make_rows()
    rows = strip_column(rows, "tag")
    rows = remove_prefix(rows, "tag", "[")
    rows = remove_suffix(rows, "tag", "]")
    result = list(rows)
    assert result[0]["tag"] == "hello"
    assert result[1]["tag"] == "world"
    assert result[2]["tag"] == ""


def test_chain_preserves_all_rows():
    rows = _make_rows()
    rows = strip_column(rows, "tag")
    result = list(rows)
    assert len(result) == 3


def test_chain_preserves_all_columns():
    rows = _make_rows()
    rows = strip_column(rows, "tag")
    rows = remove_prefix(rows, "tag", "[")
    result = list(rows)
    assert "id" in result[0]
    assert "tag" in result[0]


def test_lstrip_then_rstrip_equals_strip():
    rows = _make_rows()
    direct = list(strip_column(iter(_make_rows()), "tag"))
    chained = list(rstrip_column(lstrip_column(iter(_make_rows()), "tag"), "tag"))
    assert [r["tag"] for r in direct] == [r["tag"] for r in chained]


def test_no_mutation_across_chain():
    original = _make_rows()
    saved = [r["tag"] for r in original]
    rows = strip_column(iter(original), "tag")
    list(rows)
    assert [r["tag"] for r in original] == saved
