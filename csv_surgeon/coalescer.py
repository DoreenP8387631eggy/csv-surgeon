"""Coalescer: return first non-empty value across multiple columns."""
from typing import Iterator, List, Dict


def coalesce_columns(
    rows: Iterator[Dict[str, str]],
    columns: List[str],
    output_column: str,
    default: str = "",
) -> Iterator[Dict[str, str]]:
    """For each row, set output_column to the first non-empty value among columns."""
    for row in rows:
        value = default
        for col in columns:
            v = row.get(col, "").strip()
            if v:
                value = v
                break
        yield {**row, output_column: value}


def coalesce_fill(
    rows: Iterator[Dict[str, str]],
    column: str,
    fallbacks: List[str],
) -> Iterator[Dict[str, str]]:
    """Fill empty values in column from fallback columns in order."""
    for row in rows:
        result = dict(row)
        if not result.get(column, "").strip():
            for fb in fallbacks:
                v = result.get(fb, "").strip()
                if v:
                    result[column] = v
                    break
        yield result


def first_valid(
    rows: Iterator[Dict[str, str]],
    columns: List[str],
    output_column: str,
    predicate=lambda v: v.strip() != "",
) -> Iterator[Dict[str, str]]:
    """Set output_column to first value in columns satisfying predicate."""
    for row in rows:
        value = ""
        for col in columns:
            v = row.get(col, "")
            if predicate(v):
                value = v
                break
        yield {**row, output_column: value}
