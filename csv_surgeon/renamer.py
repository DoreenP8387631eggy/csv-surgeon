"""Bulk column renaming utilities for csv-surgeon."""

from typing import Dict, Iterator


def rename_columns(rows: Iterator[dict], mapping: Dict[str, str]) -> Iterator[dict]:
    """Rename multiple columns at once using a mapping of old->new names.

    Columns not present in the mapping are left unchanged.
    Keys in the mapping that don't exist in a row are silently ignored.

    Args:
        rows: An iterator of row dicts.
        mapping: A dict mapping old column names to new column names.

    Yields:
        Row dicts with columns renamed according to the mapping.
    """
    for row in rows:
        yield {
            mapping.get(key, key): value
            for key, value in row.items()
        }


def prefix_columns(rows: Iterator[dict], prefix: str, exclude: list = None) -> Iterator[dict]:
    """Add a prefix to every column name, optionally excluding some columns.

    Args:
        rows: An iterator of row dicts.
        prefix: String to prepend to each column name.
        exclude: List of column names to leave unchanged.

    Yields:
        Row dicts with prefixed column names.
    """
    excluded = set(exclude or [])
    for row in rows:
        yield {
            (key if key in excluded else f"{prefix}{key}"): value
            for key, value in row.items()
        }


def suffix_columns(rows: Iterator[dict], suffix: str, exclude: list = None) -> Iterator[dict]:
    """Add a suffix to every column name, optionally excluding some columns.

    Args:
        rows: An iterator of row dicts.
        suffix: String to append to each column name.
        exclude: List of column names to leave unchanged.

    Yields:
        Row dicts with suffixed column names.
    """
    excluded = set(exclude or [])
    for row in rows:
        yield {
            (key if key in excluded else f"{key}{suffix}"): value
            for key, value in row.items()
        }
