import pytest
from csv_surgeon.transposer import transpose_rows, columns_to_rows, rows_to_columns


@pytest.fixture
def wide_rows():
    return [
        {"id": "1", "name": "Alice", "age": "30"},
        {"id": "2", "name": "Bob", "age": "25"},
    ]


@pytest.fixture
def long_rows():
    return [
        {"id": "1", "column": "name", "value": "Alice"},
        {"id": "1", "column": "age", "value": "30"},
        {"id": "2", "column": "name", "value": "Bob"},
        {"id": "2", "column": "age", "value": "25"},
    ]


def test_transpose_rows_count(wide_rows):
    result = transpose_rows(iter(wide_rows))
    # 2 rows * 3 columns each
    assert len(result) == 6


def test_transpose_rows_keys(wide_rows):
    result = transpose_rows(iter(wide_rows))
    assert all("row" in r and "field" in r and "value" in r for r in result)


def test_transpose_rows_custom_column_names(wide_rows):
    result = transpose_rows(iter(wide_rows), key_column="k", value_column="v")
    assert "k" in result[0] and "v" in result[0]


def test_transpose_rows_values(wide_rows):
    result = transpose_rows(iter(wide_rows))
    name_entry = next(r for r in result if r["field"] == "name" and r["row"] == "0")
    assert name_entry["value"] == "Alice"


def test_columns_to_rows_count(wide_rows):
    result = list(columns_to_rows(wide_rows, id_column="id"))
    # 2 rows * 2 non-id columns
    assert len(result) == 4


def test_columns_to_rows_structure(wide_rows):
    result = list(columns_to_rows(wide_rows, id_column="id"))
    assert all({"id", "column", "value"} == set(r.keys()) for r in result)


def test_columns_to_rows_values(wide_rows):
    result = list(columns_to_rows(wide_rows, id_column="id"))
    age_row = next(r for r in result if r["id"] == "1" and r["column"] == "age")
    assert age_row["value"] == "30"


def test_rows_to_columns_roundtrip(wide_rows):
    long = list(columns_to_rows(wide_rows, id_column="id"))
    restored = rows_to_columns(iter(long), id_column="id")
    assert len(restored) == 2
    assert restored[0]["name"] == "Alice"
    assert restored[1]["age"] == "25"


def test_rows_to_columns_preserves_id(long_rows):
    result = rows_to_columns(iter(long_rows), id_column="id")
    assert result[0]["id"] == "1"
    assert result[1]["id"] == "2"


def test_rows_to_columns_order(long_rows):
    result = rows_to_columns(iter(long_rows), id_column="id")
    assert [r["id"] for r in result] == ["1", "2"]
