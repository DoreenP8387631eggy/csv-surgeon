"""Column type conversion transforms for CSV rows."""
from typing import Callable, Iterator


def to_int(column: str) -> Callable:
    """Convert a column's value to an integer string, or '' on failure."""
    def _transform(row: dict) -> dict:
        if column not in row:
            return row
        try:
            row[column] = str(int(float(row[column])))
        except (ValueError, TypeError):
            row[column] = ""
        return row
    return _transform


def to_float(column: str, precision: int = None) -> Callable:
    """Convert a column's value to a float string, or '' on failure."""
    def _transform(row: dict) -> dict:
        if column not in row:
            return row
        try:
            val = float(row[column])
            if precision is not None:
                row[column] = f"{val:.{precision}f}"
            else:
                row[column] = str(val)
        except (ValueError, TypeError):
            row[column] = ""
        return row
    return _transform


def to_upper(column: str) -> Callable:
    """Convert a column's value to uppercase."""
    def _transform(row: dict) -> dict:
        if column in row:
            row[column] = row[column].upper()
        return row
    return _transform


def to_lower(column: str) -> Callable:
    """Convert a column's value to lowercase."""
    def _transform(row: dict) -> dict:
        if column in row:
            row[column] = row[column].lower()
        return row
    return _transform


def strip_whitespace(column: str) -> Callable:
    """Strip leading/trailing whitespace from a column's value."""
    def _transform(row: dict) -> dict:
        if column in row:
            row[column] = row[column].strip()
        return row
    return _transform


def apply_conversions(
    rows: Iterator[dict], transforms: list
) -> Iterator[dict]:
    """Apply a list of conversion transforms to each row in the stream."""
    for row in rows:
        for transform in transforms:
            row = transform(row)
        yield row
