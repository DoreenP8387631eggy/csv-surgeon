"""Integration tests for combiner chained with other modules."""

import pytest
from csv_surgeon.combiner import combine_template, combine_columns
from csv_surgeon.filters import equals
from csv_surgeon.pipeline import FilterPipeline


@pytest.fixture
def employee_rows():
    return [
        {"first": "Alice", "last": "Smith", "dept": "eng"},
        {"first": "Bob", "last": "Jones", "dept": "hr"},
        {"first": "Carol", "last": "White", "dept": "eng"},
    ]


def test_combine_then_filter_by_combined(employee_rows):
    combined = list(combine_template(employee_rows, "{first} {last}", output_col="full"))
    result = [r for r in combined if r["full"] == "Alice Smith"]
    assert len(result) == 1


def test_combine_preserves_all_rows(employee_rows):
    result = list(combine_columns(employee_rows, ["first", "last"]))
    assert len(result) == len(employee_rows)


def test_combine_preserves_all_columns(employee_rows):
    result = list(combine_columns(employee_rows, ["first", "last"]))
    assert "dept" in result[0]
    assert "first" in result[0]


def test_chain_two_combines(employee_rows):
    step1 = combine_columns(employee_rows, ["first", "last"], output_col="full_name")
    step2 = list(
        combine_template(step1, "{full_name} ({dept})", output_col="display")
    )
    assert step2[0]["display"] == "Alice Smith (eng)"


def test_combine_with_filter_pipeline(employee_rows):
    pipeline = FilterPipeline()
    pipeline.add_filter(equals("dept", "eng"))
    combined = list(combine_columns(employee_rows, ["first", "last"]))
    result = list(pipeline.run(iter(combined)))
    assert len(result) == 2
    assert all(r["dept"] == "eng" for r in result)
