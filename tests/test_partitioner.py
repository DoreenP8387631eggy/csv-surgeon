import pytest
from csv_surgeon.partitioner import (
    partition_by_column,
    partition_by_predicate,
    stream_partitions,
    partition_counts,
)


@pytest.fixture
def sample_rows():
    return [
        {"region": "north", "sales": "100"},
        {"region": "south", "sales": "200"},
        {"region": "north", "sales": "150"},
        {"region": "east",  "sales": "80"},
        {"region": "south", "sales": "60"},
    ]


def test_partition_by_column_creates_correct_keys(sample_rows):
    result = partition_by_column(sample_rows, "region")
    assert set(result.keys()) == {"north", "south", "east"}


def test_partition_by_column_correct_counts(sample_rows):
    result = partition_by_column(sample_rows, "region")
    assert len(result["north"]) == 2
    assert len(result["south"]) == 2
    assert len(result["east"]) == 1


def test_partition_by_column_preserves_rows(sample_rows):
    result = partition_by_column(sample_rows, "region")
    assert result["north"][0]["sales"] == "100"


def test_partition_missing_column_uses_empty_string():
    rows = [{"x": "1"}, {"region": "north", "x": "2"}]
    result = partition_by_column(rows, "region")
    assert "" in result
    assert len(result[""] ) == 1


def test_partition_by_predicate_assigns_labels(sample_rows):
    predicates = [
        ("high", lambda r: int(r["sales"]) >= 100),
        ("low",  lambda r: int(r["sales"]) < 100),
    ]
    result = partition_by_predicate(sample_rows, predicates)
    assert len(result["high"]) == 3
    assert len(result["low"]) == 2


def test_partition_by_predicate_default_label(sample_rows):
    result = partition_by_predicate(sample_rows, [], default_label="all")
    assert "all" in result
    assert len(result["all"]) == 5


def test_partition_by_predicate_first_match_wins(sample_rows):
    predicates = [
        ("any", lambda r: True),
        ("never", lambda r: True),
    ]
    result = partition_by_predicate(sample_rows, predicates)
    assert "any" in result
    assert "never" not in result


def test_stream_partitions_yields_key_row_tuples(sample_rows):
    pairs = list(stream_partitions(sample_rows, "region"))
    assert len(pairs) == 5
    keys = [k for k, _ in pairs]
    assert keys[0] == "north"
    assert keys[1] == "south"


def test_partition_counts(sample_rows):
    buckets = partition_by_column(sample_rows, "region")
    counts = partition_counts(buckets)
    assert counts == {"north": 2, "south": 2, "east": 1}


def test_partition_empty_stream():
    result = partition_by_column([], "region")
    assert result == {}
