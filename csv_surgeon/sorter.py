"""Streaming-friendly CSV row sorter.

Because true streaming sort requires buffering all rows (sort is not
one-pass), we collect rows into memory, sort them, then yield them back.
For very large files the caller should consider external sort strategies.
"""

from __future__ import annotations

from typing import Iterable, Iterator


def sort_rows(
    rows: Iterable[dict],
    key: str,
    reverse: bool = False,
    numeric: bool = False,
) -> Iterator[dict]:
    """Sort *rows* by *key*.

    Args:
        rows:    Iterable of row dicts (as produced by StreamingCSVReader).
        key:     Column name to sort by.
        reverse: If True, sort descending.
        numeric: If True, cast values to float before comparing.
                 Rows where the value cannot be cast are sorted last.

    Yields:
        Row dicts in sorted order.
    """
    def sort_key(row: dict):
        value = row.get(key, "")
        if numeric:
            try:
                return (0, float(value))
            except (ValueError, TypeError):
                return (1, 0.0)
        return (0, str(value))

    buffered = list(rows)
    buffered.sort(key=sort_key, reverse=reverse)
    yield from buffered


def sort_rows_multi(
    rows: Iterable[dict],
    keys: list[tuple[str, bool]],
    numeric: bool = False,
) -> Iterator[dict]:
    """Sort *rows* by multiple columns.

    Args:
        rows:    Iterable of row dicts.
        keys:    List of (column_name, reverse) tuples applied left-to-right.
        numeric: Apply numeric casting to all key columns.

    Yields:
        Row dicts in sorted order.
    """
    if not keys:
        yield from rows
        return

    buffered = list(rows)

    # Python's sort is stable, so we sort from least significant to most
    # significant key.
    for col, reverse in reversed(keys):
        def _make_key(column: str, use_numeric: bool):
            def _key(row: dict):
                value = row.get(column, "")
                if use_numeric:
                    try:
                        return (0, float(value))
                    except (ValueError, TypeError):
                        return (1, 0.0)
                return (0, str(value))
            return _key

        buffered.sort(key=_make_key(col, numeric), reverse=reverse)

    yield from buffered
