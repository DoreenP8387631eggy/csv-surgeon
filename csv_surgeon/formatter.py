"""Column value formatting transforms."""
from typing import Callable, Iterator


def format_column(column: str, template: str) -> Callable:
    """Format a column value using a Python format string. Use {value} as placeholder."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = dict(row)
                row[column] = template.format(value=row[column])
            yield row
    return _transform


def zero_pad(column: str, width: int) -> Callable:
    """Zero-pad numeric strings in a column to a given width."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = dict(row)
                val = row[column].strip()
                if val.lstrip('-').isdigit():
                    row[column] = val.zfill(width)
            yield row
    return _transform


def number_format(column: str, decimals: int = 2, thousands_sep: bool = False) -> Callable:
    """Format a numeric column to a fixed number of decimal places."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = dict(row)
                try:
                    num = float(row[column])
                    if thousands_sep:
                        row[column] = f"{num:,.{decimals}f}"
                    else:
                        row[column] = f"{num:.{decimals}f}"
                except (ValueError, TypeError):
                    pass
            yield row
    return _transform


def date_reformat(column: str, from_fmt: str, to_fmt: str) -> Callable:
    """Reformat a date string from one format to another."""
    from datetime import datetime

    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row:
                row = dict(row)
                try:
                    dt = datetime.strptime(row[column].strip(), from_fmt)
                    row[column] = dt.strftime(to_fmt)
                except (ValueError, TypeError):
                    pass
            yield row
    return _transform
