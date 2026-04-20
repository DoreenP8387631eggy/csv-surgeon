"""Route rows to different outputs based on predicates."""
from typing import Callable, Dict, Iterable, Iterator, List, Tuple

Row = Dict[str, str]
Predicate = Callable[[Row], bool]


def route_rows(
    rows: Iterable[Row],
    rules: List[Tuple[str, Predicate]],
    default_label: str = "default",
) -> Dict[str, List[Row]]:
    """Route each row to a bucket based on the first matching predicate.

    Args:
        rows: iterable of row dicts
        rules: ordered list of (label, predicate) pairs
        default_label: bucket name when no rule matches

    Returns:
        dict mapping label -> list of rows
    """
    buckets: Dict[str, List[Row]] = {label: [] for label, _ in rules}
    buckets[default_label] = []

    for row in rows:
        placed = False
        for label, predicate in rules:
            if predicate(row):
                buckets[label].append(row)
                placed = True
                break
        if not placed:
            buckets[default_label].append(row)

    return buckets


def route_rows_stream(
    rows: Iterable[Row],
    rules: List[Tuple[str, Predicate]],
    default_label: str = "default",
) -> Iterator[Tuple[str, Row]]:
    """Stream (label, row) pairs without buffering all rows."""
    for row in rows:
        placed = False
        for label, predicate in rules:
            if predicate(row):
                yield label, row
                placed = True
                break
        if not placed:
            yield default_label, row


def build_rule(column: str, value: str, label: str) -> Tuple[str, Predicate]:
    """Convenience: build a rule that matches column == value."""
    return label, lambda row, c=column, v=value: row.get(c, "") == v


def build_contains_rule(column: str, substring: str, label: str) -> Tuple[str, Predicate]:
    """Convenience: build a rule that matches column contains substring."""
    return label, lambda row, c=column, s=substring: s in row.get(c, "")
