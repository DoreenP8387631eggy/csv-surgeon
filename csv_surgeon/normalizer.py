"""Column value normalization transforms for CSV rows."""

import re
from typing import Iterator


def strip_whitespace(column: str):
    """Strip leading/trailing whitespace from a column's values."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = {**row, column: row[column].strip()}
            yield row
    return _transform


def normalize_whitespace(column: str):
    """Collapse internal whitespace runs to a single space and strip ends."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                collapsed = re.sub(r'\s+', ' ', row[column]).strip()
                row = {**row, column: collapsed}
            yield row
    return _transform


def to_lowercase(column: str):
    """Convert a column's values to lowercase."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = {**row, column: row[column].lower()}
            yield row
    return _transform


def to_titlecase(column: str):
    """Convert a column's values to title case."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = {**row, column: row[column].title()}
            yield row
    return _transform


def remove_non_alphanumeric(column: str, keep_spaces: bool = False):
    """Remove non-alphanumeric characters from a column's values."""
    pattern = r'[^a-zA-Z0-9 ]' if keep_spaces else r'[^a-zA-Z0-9]'

    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = {**row, column: re.sub(pattern, '', row[column])}
            yield row
    return _transform


def fill_empty(column: str, default: str = ''):
    """Replace empty or whitespace-only values with a default."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row and not row[column].strip():
                row = {**row, column: default}
            yield row
    return _transform
