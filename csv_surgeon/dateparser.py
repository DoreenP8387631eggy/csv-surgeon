"""Date parsing and formatting utilities for CSV columns."""
from __future__ import annotations
from datetime import datetime
from typing import Iterable, Iterator, Callable

_DEFAULT_FORMATS = [
    "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y",
    "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y", "%Y%m%d",
]


def _parse(value: str, formats: list[str]) -> datetime | None:
    for fmt in formats:
        try:
            return datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_date_column(
    rows: Iterable[dict],
    column: str,
    output_column: str | None = None,
    formats: list[str] | None = None,
    default: str = "",
) -> Iterator[dict]:
    """Parse a date string column into ISO format (YYYY-MM-DD)."""
    fmts = formats or _DEFAULT_FORMATS
    out = output_column or column

    def _transform(row: dict) -> dict:
        r = dict(row)
        raw = r.get(column, "")
        dt = _parse(raw, fmts)
        r[out] = dt.strftime("%Y-%m-%d") if dt else default
        return r

    return (_transform(row) for row in rows)


def format_date_column(
    rows: Iterable[dict],
    column: str,
    output_format: str,
    input_formats: list[str] | None = None,
    output_column: str | None = None,
    default: str = "",
) -> Iterator[dict]:
    """Reformat a date column from any recognised format to output_format."""
    fmts = input_formats or _DEFAULT_FORMATS
    out = output_column or column

    def _transform(row: dict) -> dict:
        r = dict(row)
        raw = r.get(column, "")
        dt = _parse(raw, fmts)
        r[out] = dt.strftime(output_format) if dt else default
        return r

    return (_transform(row) for row in rows)


def extract_date_part(
    rows: Iterable[dict],
    column: str,
    part: str,
    output_column: str | None = None,
    input_formats: list[str] | None = None,
    default: str = "",
) -> Iterator[dict]:
    """Extract year/month/day/weekday from a date column."""
    fmts = input_formats or _DEFAULT_FORMATS
    out = output_column or f"{column}_{part}"
    _parts: dict[str, Callable[[datetime], str]] = {
        "year": lambda d: str(d.year),
        "month": lambda d: str(d.month),
        "day": lambda d: str(d.day),
        "weekday": lambda d: d.strftime("%A"),
        "quarter": lambda d: str((d.month - 1) // 3 + 1),
    }
    getter = _parts.get(part)

    def _transform(row: dict) -> dict:
        r = dict(row)
        raw = r.get(column, "")
        dt = _parse(raw, fmts)
        r[out] = getter(dt) if (dt and getter) else default
        return r

    return (_transform(row) for row in rows)
