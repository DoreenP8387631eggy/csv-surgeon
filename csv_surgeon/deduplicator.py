"""Deduplication utilities for CSV rows."""

from typing import Iterator, Iterable, Optional, List


def deduplicate(
    rows: Iterable[dict],
    key_columns: Optional[List[str]] = None,
) -> Iterator[dict]:
    """Yield rows with duplicates removed.

    Args:
        rows: Iterable of row dicts.
        key_columns: Columns to use as the uniqueness key. If None, all
                     columns are used.

    Yields:
        Unique rows in the order they first appear.
    """
    seen: set = set()
    for row in rows:
        if key_columns is not None:
            key = tuple(row.get(col, "") for col in key_columns)
        else:
            key = tuple(sorted(row.items()))
        if key not in seen:
            seen.add(key)
            yield row


def deduplicate_sorted(
    rows: Iterable[dict],
    key_columns: Optional[List[str]] = None,
) -> Iterator[dict]:
    """Yield rows with consecutive duplicates removed (assumes pre-sorted input).

    Useful for very large files where memory for a full seen-set is a concern,
    provided the data has already been sorted on the key columns.

    Args:
        rows: Iterable of row dicts (must be sorted on key_columns).
        key_columns: Columns to use as the uniqueness key. If None, all
                     columns are used.

    Yields:
        Rows where consecutive duplicates are dropped.
    """
    last_key = object()  # sentinel
    for row in rows:
        if key_columns is not None:
            key = tuple(row.get(col, "") for col in key_columns)
        else:
            key = tuple(sorted(row.items()))
        if key != last_key:
            last_key = key
            yield row
