"""Integration tests: pivot then melt round-trip."""
import pytest
from csv_surgeon.pivotter import pivot_rows, melt_rows


@pytest.fixture
def original_rows():
    return [
        {"region": "north", "product": "apples", "sales": "100"},
        {"region": "north", "product": "bananas", "sales": "200"},
        {"region": "south", "product": "apples", "sales": "150"},
        {"region": "south", "product": "bananas", "sales": "250"},
    ]


@pytest.fixture
def pivoted_rows(original_rows):
    """Return the pivoted form of original_rows for reuse across tests."""
    return pivot_rows(original_rows, "region", "product", "sales")


def test_pivot_produces_two_rows(pivoted_rows):
    assert len(pivoted_rows) == 2


def test_pivot_then_melt_restores_row_count(original_rows, pivoted_rows):
    melted = list(melt_rows(iter(pivoted_rows), id_cols=["region"], value_cols=["apples", "bananas"],
                            var_name="product", value_name="sales"))
    assert len(melted) == len(original_rows)


def test_pivot_then_melt_restores_values(pivoted_rows):
    melted = list(melt_rows(iter(pivoted_rows), id_cols=["region"], value_cols=["apples", "bananas"],
                            var_name="product", value_name="sales"))
    north_apples = next(
        r for r in melted if r["region"] == "north" and r["product"] == "apples"
    )
    assert north_apples["sales"] == "100"


def test_melt_variable_column_contains_original_headers(pivoted_rows):
    melted = list(melt_rows(iter(pivoted_rows), id_cols=["region"], value_cols=["apples", "bananas"],
                            var_name="product", value_name="sales"))
    products = {r["product"] for r in melted}
    assert products == {"apples", "bananas"}


def test_melt_empty_pivot_result():
    pivoted = pivot_rows(iter([]), "region", "product", "sales")
    melted = list(melt_rows(iter(pivoted), id_cols=["region"], value_cols=["apples"]))
    assert melted == []
