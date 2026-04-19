import pytest
from csv_surgeon.summarizer import summarize_rows, summary_to_rows


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "age": "30", "score": "88.5"},
        {"name": "Bob",   "age": "25", "score": "72.0"},
        {"name": "Carol", "age": "",   "score": "95.0"},
        {"name": "",      "age": "40", "score": "not_a_number"},
    ]


def test_summarize_count(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["age"]["count"] == 4


def test_summarize_non_empty(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["age"]["non_empty"] == 3
    assert stats["name"]["non_empty"] == 3


def test_summarize_empty(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["age"]["empty"] == 1


def test_summarize_numeric_count(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["age"]["numeric_count"] == 3
    assert stats["score"]["numeric_count"] == 3


def test_summarize_sum(sample_rows):
    stats = summarize_rows(sample_rows)
    assert abs(stats["age"]["sum"] - 95.0) < 1e-6


def test_summarize_mean(sample_rows):
    stats = summarize_rows(sample_rows)
    expected = 95.0 / 3
    assert abs(stats["age"]["mean"] - expected) < 1e-4


def test_summarize_min_max(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["age"]["min"] == 25.0
    assert stats["age"]["max"] == 40.0


def test_summarize_stddev_none_for_single_value():
    rows = [{"x": "5"}]
    stats = summarize_rows(rows)
    assert stats["x"]["stddev"] is None


def test_summarize_stddev_computed(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["age"]["stddev"] is not None
    assert stats["age"]["stddev"] > 0


def test_summarize_non_numeric_column(sample_rows):
    stats = summarize_rows(sample_rows)
    assert stats["name"]["mean"] is None
    assert stats["name"]["sum"] == 0.0


def test_summarize_column_filter(sample_rows):
    stats = summarize_rows(sample_rows, columns=["age"])
    assert "age" in stats
    assert "name" not in stats


def test_summary_to_rows_yields_one_per_column(sample_rows):
    stats = summarize_rows(sample_rows)
    rows = list(summary_to_rows(stats))
    assert len(rows) == 3


def test_summary_to_rows_has_expected_keys(sample_rows):
    stats = summarize_rows(sample_rows)
    rows = list(summary_to_rows(stats))
    expected_keys = {"column", "count", "non_empty", "empty", "numeric_count",
                     "sum", "mean", "stddev", "min", "max"}
    assert set(rows[0].keys()) == expected_keys


def test_summary_to_rows_empty_mean_for_non_numeric(sample_rows):
    stats = summarize_rows(sample_rows)
    rows = {r["column"]: r for r in summary_to_rows(stats)}
    assert rows["name"]["mean"] == ""
