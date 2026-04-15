"""Streaming CSV join utilities for merging two CSV sources on a key column."""

from typing import Dict, Generator, Iterable, Optional


def _index_rows(rows: Iterable[Dict[str, str]], key: str) -> Dict[str, Dict[str, str]]:
    """Load rows from an iterable into a dict keyed by the join column value."""
    index: Dict[str, Dict[str, str]] = {}
    for row in rows:
        k = row.get(key, "")
        if k:
            index[k] = row
    return index


def inner_join(
    left_rows: Iterable[Dict[str, str]],
    right_rows: Iterable[Dict[str, str]],
    left_key: str,
    right_key: Optional[str] = None,
    right_prefix: str = "right_",
) -> Generator[Dict[str, str], None, None]:
    """Yield merged rows where the key exists in both left and right sources."""
    if right_key is None:
        right_key = left_key

    right_index = _index_rows(right_rows, right_key)

    for left_row in left_rows:
        k = left_row.get(left_key, "")
        if k in right_index:
            merged = dict(left_row)
            for col, val in right_index[k].items():
                if col == right_key:
                    continue
                out_col = col if col not in merged else f"{right_prefix}{col}"
                merged[out_col] = val
            yield merged


def left_join(
    left_rows: Iterable[Dict[str, str]],
    right_rows: Iterable[Dict[str, str]],
    left_key: str,
    right_key: Optional[str] = None,
    right_prefix: str = "right_",
) -> Generator[Dict[str, str], None, None]:
    """Yield all left rows, enriched with right data where the key matches."""
    if right_key is None:
        right_key = left_key

    right_index = _index_rows(right_rows, right_key)

    for left_row in left_rows:
        k = left_row.get(left_key, "")
        merged = dict(left_row)
        if k in right_index:
            for col, val in right_index[k].items():
                if col == right_key:
                    continue
                out_col = col if col not in merged else f"{right_prefix}{col}"
                merged[out_col] = val
        yield merged
