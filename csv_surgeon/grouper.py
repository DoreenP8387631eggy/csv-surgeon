"""Group rows by one or more columns and compute per-group aggregates."""

from collections import defaultdict
from typing import Callable, Dict, Generator, Iterable, List, Optional


def group_by(
    rows: Iterable[Dict[str, str]],
    key_columns: List[str],
) -> Dict[tuple, List[Dict[str, str]]]:
    """Partition rows into groups keyed by the values of *key_columns*.

    Returns a dict mapping each unique key-tuple to the list of rows that
    share that key.  Order within each group matches the input order.
    """
    groups: Dict[tuple, List[Dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = tuple(row.get(col, "") for col in key_columns)
        groups[key].append(row)
    return dict(groups)


def aggregate_groups(
    groups: Dict[tuple, List[Dict[str, str]]],
    key_columns: List[str],
    aggregations: Dict[str, Callable[[List[Dict[str, str]]], str]],
) -> Generator[Dict[str, str], None, None]:
    """Yield one summary row per group.

    *aggregations* maps output column name -> callable that receives the list
    of rows in the group and returns a string value.
    """
    for key_values, group_rows in groups.items():
        out: Dict[str, str] = {}
        for col, val in zip(key_columns, key_values):
            out[col] = val
        for out_col, fn in aggregations.items():
            out[out_col] = fn(group_rows)
        yield out


# ---------------------------------------------------------------------------
# Built-in aggregation helpers
# ---------------------------------------------------------------------------

def agg_count(column: Optional[str] = None) -> Callable[[List[Dict[str, str]]], str]:
    """Return a function that counts rows (or non-empty values in *column*)."""
    def _fn(rows: List[Dict[str, str]]) -> str:
        if column is None:
            return str(len(rows))
        return str(sum(1 for r in rows if r.get(column, "").strip() != ""))
    return _fn


def agg_sum(column: str) -> Callable[[List[Dict[str, str]]], str]:
    """Return a function that sums numeric values in *column*."""
    def _fn(rows: List[Dict[str, str]]) -> str:
        total = 0.0
        for r in rows:
            try:
                total += float(r.get(column, ""))
            except (ValueError, TypeError):
                pass
        return str(total)
    return _fn


def agg_max(column: str) -> Callable[[List[Dict[str, str]]], str]:
    """Return a function that returns the maximum numeric value in *column*."""
    def _fn(rows: List[Dict[str, str]]) -> str:
        values = []
        for r in rows:
            try:
                values.append(float(r.get(column, "")))
            except (ValueError, TypeError):
                pass
        return str(max(values)) if values else ""
    return _fn


def agg_min(column: str) -> Callable[[List[Dict[str, str]]], str]:
    """Return a function that returns the minimum numeric value in *column*."""
    def _fn(rows: List[Dict[str, str]]) -> str:
        values = []
        for r in rows:
            try:
                values.append(float(r.get(column, "")))
            except (ValueError, TypeError):
                pass
        return str(min(values)) if values else ""
    return _fn
