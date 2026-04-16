"""Tests for csv_surgeon.typer."""

import pytest
from csv_surgeon.typer import infer_column_types, annotate_row, annotate_rows


@pytest.fixture
def int_rows():
    return [
        {"id": "1", "score": "42"},
        {"id": "2", "score": "7"},
    ]


@pytest.fixture
def mixed_rows():
    return [
        {"id": "1", "value": "3.14", "flag": "true", "name": "Alice"},
        {"id": "2", "value": "2.71", "flag": "false", "name": "Bob"},
    ]


def test_infer_all_ints(int_rows):
    types = infer_column_types(int_rows)
    assert types["id"] == "int"
    assert types["score"] == "int"


def test_infer_float_column():
    rows = [{"x": "1.5"}, {"x": "2.0"}]
    types = infer_column_types(rows)
    assert types["x"] == "float"


def test_infer_bool_column():
    rows = [{"active": "true"}, {"active": "false"}]
    types = infer_column_types(rows)
    assert types["active"] == "bool"


def test_infer_str_column():
    rows = [{"name": "Alice"}, {"name": "Bob"}]
    types = infer_column_types(rows)
    assert types["name"] == "str"


def test_infer_mixed_int_and_float_becomes_float():
    rows = [{"val": "1"}, {"val": "1.5"}]
    types = infer_column_types(rows)
    assert types["val"] == "float"


def test_infer_empty_rows_returns_empty():
    assert infer_column_types([]) == {}


def test_infer_skips_empty_values():
    rows = [{"x": ""}, {"x": "42"}]
    types = infer_column_types(rows)
    assert types["x"] == "int"


def test_annotate_row_casts_int():
    row = {"id": "5", "score": "99"}
    result = annotate_row(row, {"id": "int", "score": "int"})
    assert result["id"] == 5
    assert result["score"] == 99


def test_annotate_row_casts_float():
    row = {"price": "3.99"}
    result = annotate_row(row, {"price": "float"})
    assert result["price"] == pytest.approx(3.99)


def test_annotate_row_casts_bool_true():
    row = {"active": "yes"}
    result = annotate_row(row, {"active": "bool"})
    assert result["active"] is True


def test_annotate_row_casts_bool_false():
    row = {"active": "false"}
    result = annotate_row(row, {"active": "bool"})
    assert result["active"] is False


def test_annotate_row_leaves_str_unchanged():
    row = {"name": "  Alice  "}
    result = annotate_row(row, {"name": "str"})
    assert result["name"] == "  Alice  "


def test_annotate_row_empty_value_unchanged():
    row = {"x": ""}
    result = annotate_row(row, {"x": "int"})
    assert result["x"] == ""


def test_annotate_rows_lazy(mixed_rows):
    type_map = infer_column_types(mixed_rows)
    results = list(annotate_rows(iter(mixed_rows), type_map))
    assert results[0]["id"] == 1
    assert results[0]["value"] == pytest.approx(3.14)
    assert results[0]["flag"] is True
    assert results[0]["name"] == "Alice"
