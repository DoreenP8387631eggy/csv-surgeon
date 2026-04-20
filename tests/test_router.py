import pytest
from csv_surgeon.router import (
    route_rows,
    route_rows_stream,
    build_rule,
    build_contains_rule,
)


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "dept": "eng", "city": "London"},
        {"name": "Bob", "dept": "hr", "city": "Paris"},
        {"name": "Carol", "dept": "eng", "city": "Berlin"},
        {"name": "Dave", "dept": "sales", "city": "London"},
        {"name": "Eve", "dept": "hr", "city": "Rome"},
    ]


def test_route_rows_correct_buckets(sample_rows):
    rules = [build_rule("dept", "eng", "engineering"), build_rule("dept", "hr", "human_resources")]
    result = route_rows(sample_rows, rules)
    assert len(result["engineering"]) == 2
    assert len(result["human_resources"]) == 2


def test_route_rows_default_bucket(sample_rows):
    rules = [build_rule("dept", "eng", "engineering")]
    result = route_rows(sample_rows, rules)
    assert len(result["default"]) == 3


def test_route_rows_custom_default_label(sample_rows):
    rules = [build_rule("dept", "eng", "engineering")]
    result = route_rows(sample_rows, rules, default_label="other")
    assert "other" in result
    assert len(result["other"]) == 3


def test_route_rows_first_match_wins(sample_rows):
    rules = [
        build_rule("dept", "eng", "technical"),
        build_rule("city", "London", "london"),
    ]
    result = route_rows(sample_rows, rules)
    # Alice is eng AND London — should go to 'technical'
    technical_names = [r["name"] for r in result["technical"]]
    assert "Alice" in technical_names
    london_names = [r["name"] for r in result["london"]]
    assert "Alice" not in london_names
    assert "Dave" in london_names


def test_route_rows_all_rows_accounted_for(sample_rows):
    rules = [build_rule("dept", "eng", "eng"), build_rule("dept", "hr", "hr")]
    result = route_rows(sample_rows, rules)
    total = sum(len(v) for v in result.values())
    assert total == len(sample_rows)


def test_build_contains_rule(sample_rows):
    rules = [build_contains_rule("city", "on", "on_city")]
    result = route_rows(sample_rows, rules)
    on_city_names = [r["name"] for r in result["on_city"]]
    assert "Alice" in on_city_names   # London
    assert "Dave" in on_city_names    # London
    assert "Bob" not in on_city_names  # Paris


def test_route_rows_stream_yields_labels(sample_rows):
    rules = [build_rule("dept", "eng", "eng")]
    pairs = list(route_rows_stream(sample_rows, rules))
    labels = [label for label, _ in pairs]
    assert labels.count("eng") == 2
    assert labels.count("default") == 3


def test_route_rows_stream_preserves_row_data(sample_rows):
    rules = [build_rule("dept", "hr", "hr")]
    pairs = list(route_rows_stream(sample_rows, rules))
    hr_rows = [row for label, row in pairs if label == "hr"]
    assert hr_rows[0]["name"] == "Bob"
    assert hr_rows[1]["name"] == "Eve"


def test_route_rows_empty_input():
    rules = [build_rule("dept", "eng", "eng")]
    result = route_rows([], rules)
    assert result["eng"] == []
    assert result["default"] == []


def test_route_rows_no_rules(sample_rows):
    result = route_rows(sample_rows, [], default_label="all")
    assert len(result["all"]) == len(sample_rows)
