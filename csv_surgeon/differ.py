"""Row-level diff utilities for comparing two CSV streams."""
from typing import Iterator, Dict, List, Optional


def _row_sig(row: Dict[str, str], columns: Optional[List[str]] = None) -> tuple:
    if columns:
        return tuple(row.get(c, "") for c in columns)
    return tuple(sorted(row.items()))


def unified_diff(
    before: Iterator[Dict[str, str]],
    after: Iterator[Dict[str, str]],
    key_column: str,
    track_columns: Optional[List[str]] = None,
) -> Iterator[Dict[str, str]]:
    """Yield rows annotated with _diff_status: added, removed, changed, unchanged."""
    before_index: Dict[str, Dict[str, str]] = {r[key_column]: r for r in before}
    after_index: Dict[str, Dict[str, str]] = {r[key_column]: r for r in after}

    all_keys = list(before_index) + [k for k in after_index if k not in before_index]

    for key in all_keys:
        b = before_index.get(key)
        a = after_index.get(key)
        if b is None:
            yield {**a, "_diff_status": "added"}
        elif a is None:
            yield {**b, "_diff_status": "removed"}
        elif _row_sig(b, track_columns) != _row_sig(a, track_columns):
            yield {**a, "_diff_status": "changed"}
        else:
            yield {**a, "_diff_status": "unchanged"}


def only_changed(
    rows: Iterator[Dict[str, str]],
) -> Iterator[Dict[str, str]]:
    """Filter unified_diff output to only added/removed/changed rows."""
    for row in rows:
        if row.get("_diff_status", "unchanged") != "unchanged":
            yield row


def diff_summary(rows: Iterator[Dict[str, str]]) -> Dict[str, int]:
    """Consume a unified_diff stream and return counts per status."""
    counts: Dict[str, int] = {"added": 0, "removed": 0, "changed": 0, "unchanged": 0}
    for row in rows:
        status = row.get("_diff_status", "unchanged")
        counts[status] = counts.get(status, 0) + 1
    return counts
