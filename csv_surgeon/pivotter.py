"""Pivot and unpivot (melt) operations for CSV rows."""
from typing import Iterator, List, Dict, Any, Optional


def pivot_rows(
    rows: Iterator[Dict[str, Any]],
    index_col: str,
    pivot_col: str,
    value_col: str,
) -> List[Dict[str, Any]]:
    """Pivot rows: turn unique values in pivot_col into new columns.

    Args:
        rows: iterable of row dicts.
        index_col: column whose values become the row identifiers.
        pivot_col: column whose unique values become new column headers.
        value_col: column whose values fill the pivoted cells.

    Returns:
        List of aggregated row dicts.
    """
    buckets: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        key = row.get(index_col, "")
        pivot_key = row.get(pivot_col, "")
        value = row.get(value_col, "")
        if key not in buckets:
            buckets[key] = {index_col: key}
        buckets[key][pivot_key] = value
    return list(buckets.values())


def melt_rows(
    rows: Iterator[Dict[str, Any]],
    id_cols: List[str],
    value_cols: Optional[List[str]] = None,
    var_name: str = "variable",
    value_name: str = "value",
) -> Iterator[Dict[str, Any]]:
    """Unpivot (melt) rows: turn column headers into row values.

    Args:
        rows: iterable of row dicts.
        id_cols: columns to keep as identifiers.
        value_cols: columns to melt; if None, all non-id columns are melted.
        var_name: name for the new variable column.
        value_name: name for the new value column.

    Yields:
        One row per id/variable combination.
    """
    for row in rows:
        id_part = {col: row.get(col, "") for col in id_cols}
        cols_to_melt = value_cols if value_cols is not None else [
            c for c in row.keys() if c not in id_cols
        ]
        for col in cols_to_melt:
            melted = dict(id_part)
            melted[var_name] = col
            melted[value_name] = row.get(col, "")
            yield melted
