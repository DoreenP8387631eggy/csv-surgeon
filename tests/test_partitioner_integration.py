"""Integration: partition -> recombine and verify totals."""
from csv_surgeon.partitioner import (
    partition_by_column,
    partition_by_predicate,
    partition_counts,
    stream_partitions,
)


def _make_rows():
    return [
        {"dept": "eng",  "salary": "90000"},
        {"dept": "hr",   "salary": "60000"},
        {"dept": "eng",  "salary": "95000"},
        {"dept": "eng",  "salary": "85000"},
        {"dept": "hr",   "salary": "62000"},
        {"dept": "sales","salary": "70000"},
    ]


def test_partition_then_recombine_preserves_all_rows():
    rows = _make_rows()
    buckets = partition_by_column(rows, "dept")
    all_rows = [r for bucket in buckets.values() for r in bucket]
    assert len(all_rows) == len(rows)


def test_partition_counts_sum_equals_total():
    rows = _make_rows()
    buckets = partition_by_column(rows, "dept")
    counts = partition_counts(buckets)
    assert sum(counts.values()) == len(rows)


def test_predicate_partition_covers_all_rows():
    rows = _make_rows()
    predicates = [
        ("high", lambda r: int(r["salary"]) >= 80000),
        ("mid",  lambda r: int(r["salary"]) >= 65000),
    ]
    buckets = partition_by_predicate(rows, predicates, default_label="low")
    total = sum(len(v) for v in buckets.values())
    assert total == len(rows)


def test_stream_partitions_no_data_loss():
    rows = _make_rows()
    pairs = list(stream_partitions(rows, "dept"))
    assert len(pairs) == len(rows)
    assert all(isinstance(k, str) for k, _ in pairs)
