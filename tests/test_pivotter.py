"""Tests for csv_surgeon.pivotter (pivot and melt operations)."""
import pytest
from csv_surgeon.pivotter import pivot_rows, melt_rows


@pytest.fixture
def sales_rows():
    return [
        {"region": "north", "product": "apples", "sales": "100"},
        {"region": "north", "product": "bananas", "sales": "200"},
        {"region": "south", "product": "apples", "sales": "150"},
        {"region": "south", "product": "bananas", "sales": "250"},
    ]


@pytest.fixture
def wide_rows():
    return [
        {"id": "1", "name": "Alice", "jan": "10", "feb": "20"},
        {"id": "2", "name": "Bob", "jan": "30", "feb": "40"},
    ]


def test_pivot_rows_creates_new_columns(sales_rows):
    result = pivot_rows(sales_rows, index_col="region", pivot_col="product", value_col="sales")
    assert len(result) == 2


def test_pivot_rows_correct_values(sales_rows):
    result = pivot_rows(sales_rows, index_col="region", pivot_col="product", value_col="sales")
    north = next(r for r in result if r["region"] == "north")
    assert north["apples"] == "100"
    assert north["bananas"] == "200"


def test_pivot_rows_preserves_index(sales_rows):
    result = pivot_rows(sales_rows, index_col="region", pivot_col="product", value_col="sales")
    regions = {r["region"] for r in result}
    assert regions == {"north", "south"}


def test_pivot_rows_empty_input():
    result = pivot_rows(iter([]), index_col="region", pivot_col="product", value_col="sales")
    assert result == []


def test_pivot_rows_single_row():
    rows = [{"region": "east", "product": "apples", "sales": "50"}]
    result = pivot_rows(iter(rows), index_col="region", pivot_col="product", value_col="sales")
    assert result == [{"region": "east", "apples": "50"}]


def test_melt_rows_produces_correct_count(wide_rows):
    result = list(melt_rows(iter(wide_rows), id_cols=["id", "name"], value_cols=["jan", "feb"]))
    assert len(result) == 4


def test_melt_rows_var_and_value_columns(wide_rows):
    result = list(melt_rows(iter(wide_rows), id_cols=["id", "name"], value_cols=["jan", "feb"]))
    variables = {r["variable"] for r in result}
    assert variables == {"jan", "feb"}


def test_melt_rows_preserves_id_columns(wide_rows):
    result = list(melt_rows(iter(wide_rows), id_cols=["id", "name"], value_cols=["jan"]))
    assert all("id" in r and "name" in r for r in result)


def test_melt_rows_custom_var_name(wide_rows):
    result = list(melt_rows(iter(wide_rows), id_cols=["id"], value_cols=["jan"], var_name="month", value_name="amount"))
    assert "month" in result[0]
    assert "amount" in result[0]


def test_melt_rows_auto_detect_value_cols(wide_rows):
    result = list(melt_rows(iter(wide_rows), id_cols=["id", "name"]))
    assert len(result) == 4
    variables = {r["variable"] for r in result}
    assert variables == {"jan", "feb"}


def test_melt_rows_empty_input():
    result = list(melt_rows(iter([]), id_cols=["id"], value_cols=["jan"]))
    assert result == []


def test_melt_rows_correct_value(wide_rows):
    result = list(melt_rows(iter(wide_rows), id_cols=["id", "name"], value_cols=["jan"]))
    alice = next(r for r in result if r["id"] == "1")
    assert alice["value"] == "10"
