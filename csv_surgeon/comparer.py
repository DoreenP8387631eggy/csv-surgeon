"""Row-level comparison utilities for diffing two CSV streams."""
from typing import Iterator, Dict, Any, Tuple, List, Optional


def _row_key(row: Dict[str, Any], key_columns: List[str]) -> Tuple:
    """Build a hashable key from the specified columns of a row."""
    return tuple(row.get(col, "") for col in key_columns)


def diff_rows(
    left: Iterator[Dict[str, Any]],
    right: Iterator[Dict[str, Any]],
    key_columns: List[str],
) -> Iterator[Dict[str, Any]]:
    """Yield rows that differ between left and right streams.

    Each yielded row includes a ``_diff`` column with value:
      - ``"added"``   – present in right but not in left
      - ``"removed"`` – present in left but not in right
      - ``"changed"`` – present in both but with different values
    """
    left_index: Dict[Tuple, Dict[str, Any]] = {}
    right_index: Dict[Tuple, Dict[str, Any]] = {}

    for row in left:
        left_index[_row_key(row, key_columns)] = row

    for row in right:
        right_index[_row_key(row, key_columns)] = row

    all_keys = set(left_index) | set(right_index)

    for key in all_keys:
        in_left = key in left_index
        in_right = key in right_index

        if in_left and not in_right:
            row = dict(left_index[key])
            row["_diff"] = "removed"
            yield row
        elif in_right and not in_left:
            row = dict(right_index[key])
            row["_diff"] = "added"
            yield row
        else:
            left_row = left_index[key]
            right_row = right_index[key]
            if left_row != right_row:
                row = dict(right_row)
                row["_diff"] = "changed"
                yield row


def intersect_rows(
    left: Iterator[Dict[str, Any]],
    right: Iterator[Dict[str, Any]],
    key_columns: List[str],
) -> Iterator[Dict[str, Any]]:
    """Yield rows whose keys appear in both streams (using right-side values)."""
    right_keys = {_row_key(row, key_columns) for row in right}
    for row in left:
        if _row_key(row, key_columns) in right_keys:
            yield row


def subtract_rows(
    left: Iterator[Dict[str, Any]],
    right: Iterator[Dict[str, Any]],
    key_columns: List[str],
) -> Iterator[Dict[str, Any]]:
    """Yield rows from left whose keys do NOT appear in right."""
    right_keys = {_row_key(row, key_columns) for row in right}
    for row in left:
        if _row_key(row, key_columns) not in right_keys:
            yield row
