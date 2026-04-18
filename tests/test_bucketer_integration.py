"""Integration tests: bucket then filter/aggregate."""
import pytest
from csv_surgeon.bucketer import bucket_column, quantile_bucket
from csv_surgeon.filters import equals
from csv_surgeon.pipeline import FilterPipeline


def _make_rows(n=12):
    return [{"id": str(i), "value": str(i * 10)} for i in range(n)]


def test_bucket_then_filter_low_bucket():
    rows = _make_rows(10)
    bucketed = list(bucket_column(iter(rows), "value", [0, 40, 80, 120], labels=["low", "mid", "high"]))
    pipeline = FilterPipeline()
    pipeline.add_filter(equals("bucket", "low"))
    result = list(pipeline.run(iter(bucketed)))
    assert all(r["bucket"] == "low" for r in result)
    assert len(result) == 4  # 0,10,20,30


def test_bucket_counts_sum_to_total():
    rows = _make_rows(9)
    bucketed = list(bucket_column(iter(rows), "value", [0, 30, 60, 90], labels=["a", "b", "c"]))
    from collections import Counter
    counts = Counter(r["bucket"] for r in bucketed)
    assert sum(counts.values()) == 9


def test_quantile_then_filter_q1():
    rows = [{"v": str(i)} for i in range(1, 9)]
    bucketed = list(quantile_bucket(rows, "v", n_buckets=4))
    q1 = [r for r in bucketed if r["quantile"] == "Q1"]
    assert len(q1) >= 1


def test_bucket_preserves_all_columns_through_pipeline():
    rows = [{"name": f"user{i}", "age": str(i * 5)} for i in range(1, 6)]
    result = list(bucket_column(iter(rows), "age", [0, 15, 30], labels=["young", "old"], default="oor"))
    for r in result:
        assert "name" in r and "age" in r and "bucket" in r
