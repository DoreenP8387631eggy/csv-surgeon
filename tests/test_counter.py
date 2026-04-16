"""Tests for csv_surgeon.counter."""
import pytest
from csv_surgeon.counter import count_values, count_values_multi, frequency_rows


@pytest.fixture
def sample_rows():
    return [
        {"city": "London", "country": "UK"},
        {"city": "Paris", "country": "FR"},
        {"city": "London", "country": "UK"},
        {"city": "Berlin", "country": "DE"},
        {"city": "London", "country": "UK"},
        {"city": "Paris", "country": "FR"},
    ]


def test_count_values_correct_counts(sample_rows):
    result = count_values(sample_rows, "city")
    assert result["London"] == 3
    assert result["Paris"] == 2
    assert result["Berlin"] == 1


def test_count_values_sorted_by_frequency(sample_rows):
    result = count_values(sample_rows, "city")
    counts = list(result.values())
    assert counts == sorted(counts, reverse=True)


def test_count_values_missing_column_uses_empty_string(sample_rows):
    result = count_values(sample_rows, "region")
    assert result == {"": 6}


def test_count_values_empty_stream():
    result = count_values([], "city")
    assert result == {}


def test_count_values_multi_correct_keys(sample_rows):
    result = count_values_multi(sample_rows, ["city", "country"])
    assert result[("London", "UK")] == 3
    assert result[("Paris", "FR")] == 2
    assert result[("Berlin", "DE")] == 1


def test_count_values_multi_sorted_by_frequency(sample_rows):
    result = count_values_multi(sample_rows, ["city", "country"])
    counts = list(result.values())
    assert counts == sorted(counts, reverse=True)


def test_frequency_rows_fields(sample_rows):
    rows = list(frequency_rows(sample_rows, "city"))
    assert all("value" in r and "count" in r and "percent" in r for r in rows)


def test_frequency_rows_count_values(sample_rows):
    rows = {r["value"]: int(r["count"]) for r in frequency_rows(sample_rows, "city")}
    assert rows["London"] == 3
    assert rows["Paris"] == 2
    assert rows["Berlin"] == 1


def test_frequency_rows_percent_sums_to_100(sample_rows):
    rows = list(frequency_rows(sample_rows, "city"))
    total = sum(float(r["percent"]) for r in rows)
    assert abs(total - 100.0) < 0.01


def test_frequency_rows_empty_stream():
    rows = list(frequency_rows([], "city"))
    assert rows == []
