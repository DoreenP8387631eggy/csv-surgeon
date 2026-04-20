"""Integration tests: route then process each bucket independently."""
import pytest
from csv_surgeon.router import route_rows, build_rule, build_contains_rule
from csv_surgeon.filters import equals
from csv_surgeon.aggregator import count, sum_column


def _make_rows(n=10):
    depts = ["eng", "hr", "sales"]
    return [
        {"id": str(i), "dept": depts[i % 3], "salary": str(30000 + i * 1000)}
        for i in range(n)
    ]


def test_route_then_count_per_bucket():
    rows = _make_rows(9)
    rules = [
        build_rule("dept", "eng", "eng"),
        build_rule("dept", "hr", "hr"),
        build_rule("dept", "sales", "sales"),
    ]
    buckets = route_rows(rows, rules)
    assert count(iter(buckets["eng"])) == 3
    assert count(iter(buckets["hr"])) == 3
    assert count(iter(buckets["sales"])) == 3


def test_route_then_sum_salary_per_dept():
    rows = _make_rows(6)
    rules = [build_rule("dept", "eng", "eng"), build_rule("dept", "hr", "hr")]
    buckets = route_rows(rows, rules)
    eng_sum = sum_column(iter(buckets["eng"]), "salary")
    hr_sum = sum_column(iter(buckets["hr"]), "salary")
    assert eng_sum > 0
    assert hr_sum > 0


def test_route_preserves_all_rows():
    rows = _make_rows(15)
    rules = [build_rule("dept", "eng", "eng"), build_rule("dept", "hr", "hr")]
    buckets = route_rows(rows, rules)
    total = sum(len(v) for v in buckets.values())
    assert total == 15


def test_route_contains_then_filter():
    rows = [
        {"name": "frontend-dev", "dept": "eng"},
        {"name": "backend-dev", "dept": "eng"},
        {"name": "hr-manager", "dept": "hr"},
    ]
    rules = [build_contains_rule("name", "dev", "developers")]
    buckets = route_rows(rows, rules)
    assert len(buckets["developers"]) == 2
    assert len(buckets["default"]) == 1
