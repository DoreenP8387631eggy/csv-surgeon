"""Tests for csv_surgeon.filters and FilterPipeline."""

import io
import pytest

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.filters import (
    equals, not_equals, contains, matches_regex,
    greater_than, less_than, all_of, any_of, negate,
)
from csv_surgeon.pipeline import FilterPipeline


SAMPLE_CSV = """name,age,city
Alice,30,New York
Bob,25,Los Angeles
Carol,35,New York
Dave,22,Chicago
"""


@pytest.fixture
def pipeline():
    reader = StreamingCSVReader(io.StringIO(SAMPLE_CSV))
    return FilterPipeline(reader)


def make_pipeline(csv_text: str) -> FilterPipeline:
    reader = StreamingCSVReader(io.StringIO(csv_text))
    return FilterPipeline(reader)


def test_equals_filter(pipeline):
    pipeline.add_filter(equals("city", "New York"))
    results = list(pipeline.iter_filtered())
    assert len(results) == 2
    assert all(r["city"] == "New York" for r in results)


def test_not_equals_filter(pipeline):
    pipeline.add_filter(not_equals("city", "New York"))
    results = list(pipeline.iter_filtered())
    assert len(results) == 2
    assert all(r["city"] != "New York" for r in results)


def test_contains_filter(pipeline):
    pipeline.add_filter(contains("name", "a"))
    names = [r["name"] for r in pipeline.iter_filtered()]
    # Carol and Dave contain lowercase 'a'
    assert "Carol" in names
    assert "Dave" in names


def test_matches_regex_filter(pipeline):
    pipeline.add_filter(matches_regex("name", r"^[AB]"))
    names = [r["name"] for r in pipeline.iter_filtered()]
    assert names == ["Alice", "Bob"]


def test_greater_than_filter(pipeline):
    pipeline.add_filter(greater_than("age", 28))
    results = list(pipeline.iter_filtered())
    assert all(float(r["age"]) > 28 for r in results)
    assert len(results) == 2  # Alice (30) and Carol (35)


def test_less_than_filter(pipeline):
    pipeline.add_filter(less_than("age", 26))
    results = list(pipeline.iter_filtered())
    assert len(results) == 1
    assert results[0]["name"] == "Dave"


def test_all_of_combines_filters(pipeline):
    f = all_of([equals("city", "New York"), greater_than("age", 31)])
    pipeline.add_filter(f)
    results = list(pipeline.iter_filtered())
    assert len(results) == 1
    assert results[0]["name"] == "Carol"


def test_any_of_combines_filters(pipeline):
    f = any_of([equals("name", "Alice"), equals("name", "Dave")])
    pipeline.add_filter(f)
    names = [r["name"] for r in pipeline.iter_filtered()]
    assert set(names) == {"Alice", "Dave"}


def test_negate_filter(pipeline):
    pipeline.add_filter(negate(equals("city", "New York")))
    results = list(pipeline.iter_filtered())
    assert all(r["city"] != "New York" for r in results)


def test_pipeline_count(pipeline):
    pipeline.add_filter(equals("city", "New York"))
    assert pipeline.count() == 2


def test_pipeline_exposes_headers(pipeline):
    list(pipeline.iter_filtered())
    assert pipeline.headers == ["name", "age", "city"]


def test_no_filters_yields_all_rows(pipeline):
    results = list(pipeline.iter_filtered())
    assert len(results) == 4
