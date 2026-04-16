import pytest
from csv_surgeon.tagger import (
    tag_column,
    tag_multi,
    tag_equals,
    tag_contains,
    tag_numeric_range,
)


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "dept": "Engineering", "salary": "95000"},
        {"name": "Bob", "dept": "Sales", "salary": "55000"},
        {"name": "Carol", "dept": "Engineering", "salary": "120000"},
        {"name": "Dave", "dept": "HR", "salary": "48000"},
    ]


def test_tag_column_first_match(sample_rows):
    rules = [
        tag_equals("dept", "Engineering", "tech"),
        tag_equals("dept", "Sales", "sales"),
    ]
    result = list(tag_column(sample_rows, "tag", rules, default="other"))
    assert result[0]["tag"] == "tech"
    assert result[1]["tag"] == "sales"
    assert result[3]["tag"] == "other"


def test_tag_column_default_when_no_match(sample_rows):
    rules = [tag_equals("dept", "Finance", "finance")]
    result = list(tag_column(sample_rows, "tag", rules, default="unknown"))
    assert all(r["tag"] == "unknown" for r in result)


def test_tag_column_preserves_existing_fields(sample_rows):
    rules = [tag_equals("dept", "HR", "hr")]
    result = list(tag_column(sample_rows, "tag", rules))
    assert result[0]["name"] == "Alice"
    assert result[0]["salary"] == "95000"


def test_tag_multi_all_matching_rules(sample_rows):
    rules = [
        tag_equals("dept", "Engineering", "tech"),
        tag_numeric_range("salary", 90000, 200000, "high-earner"),
    ]
    result = list(tag_multi(sample_rows, "tags", rules))
    assert result[0]["tags"] == "tech|high-earner"
    assert result[1]["tags"] == ""
    assert result[2]["tags"] == "tech|high-earner"


def test_tag_multi_separator(sample_rows):
    rules = [
        tag_equals("dept", "Engineering", "tech"),
        tag_numeric_range("salary", 90000, 200000, "high-earner"),
    ]
    result = list(tag_multi(sample_rows, "tags", rules, separator=","))
    assert result[0]["tags"] == "tech,high-earner"


def test_tag_contains_rule(sample_rows):
    rules = [tag_contains("dept", "engineer", "tech")]
    result = list(tag_column(sample_rows, "tag", rules))
    assert result[0]["tag"] == "tech"
    assert result[2]["tag"] == "tech"
    assert result[1]["tag"] == ""


def test_tag_numeric_range_rule(sample_rows):
    rules = [tag_numeric_range("salary", 50000, 100000, "mid")]
    result = list(tag_column(sample_rows, "tag", rules))
    assert result[0]["tag"] == "mid"
    assert result[1]["tag"] == "mid"
    assert result[2]["tag"] == ""
    assert result[3]["tag"] == ""


def test_tag_numeric_range_non_numeric_skipped():
    rows = [{"val": "abc"}, {"val": "50"}, {"val": ""}]
    rules = [tag_numeric_range("val", 0, 100, "ok")]
    result = list(tag_column(rows, "tag", rules))
    assert result[0]["tag"] == ""
    assert result[1]["tag"] == "ok"
    assert result[2]["tag"] == ""


def test_tag_column_empty_stream():
    result = list(tag_column([], "tag", [], default="x"))
    assert result == []
