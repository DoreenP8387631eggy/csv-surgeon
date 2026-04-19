"""Column compactor: merge sparse columns into a single dense column."""
from typing import Iterator, Dict, Any, List, Optional


def compact_columns(
    rows: Iterator[Dict[str, Any]],
    columns: List[str],
    output_col: str = "compacted",
    separator: str = ",",
    skip_empty: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Merge multiple columns into one by joining non-empty values."""
    for row in rows:
        parts = []
        for col in columns:
            val = row.get(col, "")
            if skip_empty and not str(val).strip():
                continue
            parts.append(str(val))
        out = {**row, output_col: separator.join(parts)}
        yield out


def compact_first_valid(
    rows: Iterator[Dict[str, Any]],
    columns: List[str],
    output_col: str = "compacted",
    default: str = "",
) -> Iterator[Dict[str, Any]]:
    """Pick the first non-empty value from the given columns."""
    for row in rows:
        value = default
        for col in columns:
            val = str(row.get(col, "")).strip()
            if val:
                value = val
                break
        yield {**row, output_col: value}


def drop_empty_columns(
    rows: Iterator[Dict[str, Any]],
    columns: Optional[List[str]] = None,
) -> Iterator[Dict[str, Any]]:
    """Drop columns that are empty across all rows (requires buffering)."""
    buffered = list(rows)
    if not buffered:
        return
    candidates = columns if columns is not None else list(buffered[0].keys())
    non_empty = {
        col for col in candidates
        if any(str(r.get(col, "")).strip() for r in buffered)
    }
    for row in buffered:
        yield {k: v for k, v in row.items() if k not in candidates or k in non_empty}
