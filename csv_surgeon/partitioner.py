"""Partition rows into named buckets based on column value or predicate."""
from typing import Callable, Dict, Generator, Iterable, List, Tuple

Row = Dict[str, str]


def partition_by_column(
    rows: Iterable[Row],
    column: str,
) -> Dict[str, List[Row]]:
    """Group rows into buckets keyed by the value of *column*."""
    buckets: Dict[str, List[Row]] = {}
    for row in rows:
        key = row.get(column, "")
        buckets.setdefault(key, []).append(row)
    return buckets


def partition_by_predicate(
    rows: Iterable[Row],
    predicates: List[Tuple[str, Callable[[Row], bool]]],
    default_label: str = "other",
) -> Dict[str, List[Row]]:
    """Assign each row to the first matching predicate label.

    Rows that match no predicate go into *default_label*.
    """
    buckets: Dict[str, List[Row]] = {}
    for row in rows:
        label = default_label
        for name, pred in predicates:
            if pred(row):
                label = name
                break
        buckets.setdefault(label, []).append(row)
    return buckets


def stream_partitions(
    rows: Iterable[Row],
    column: str,
) -> Generator[Tuple[str, Row], None, None]:
    """Yield (partition_key, row) tuples without buffering all rows."""
    for row in rows:
        yield row.get(column, ""), row


def partition_counts(buckets: Dict[str, List[Row]]) -> Dict[str, int]:
    """Return a mapping of partition label -> row count."""
    return {k: len(v) for k, v in buckets.items()}
