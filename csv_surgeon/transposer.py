"""Transpose rows to columns and columns to rows."""
from typing import Iterator, List, Dict


def transpose_rows(
    rows: Iterator[Dict[str, str]],
    key_column: str = "field",
    value_column: str = "value",
) -> List[Dict[str, str]]:
    """Transpose a wide row stream into a long key/value stream.

    Each column name becomes a row with its value.  One output row is
    produced per (input-row-index, column) pair.
    """
    result = []
    for idx, row in enumerate(rows):
        for col, val in row.items():
            result.append({"row": str(idx), key_column: col, value_column: val})
    return result


def columns_to_rows(
    rows: List[Dict[str, str]],
    id_column: str,
) -> Iterator[Dict[str, str]]:
    """Pivot a table so each non-id column becomes its own row.

    Output columns: <id_column>, 'column', 'value'.
    """
    for row in rows:
        row_id = row.get(id_column, "")
        for col, val in row.items():
            if col == id_column:
                continue
            yield {id_column: row_id, "column": col, "value": val}


def rows_to_columns(
    rows: Iterator[Dict[str, str]],
    id_column: str,
    key_column: str = "column",
    value_column: str = "value",
) -> List[Dict[str, str]]:
    """Inverse of columns_to_rows – reassemble wide rows from long format."""
    buckets: Dict[str, Dict[str, str]] = {}
    order: List[str] = []
    for row in rows:
        row_id = row[id_column]
        if row_id not in buckets:
            buckets[row_id] = {id_column: row_id}
            order.append(row_id)
        buckets[row_id][row[key_column]] = row[value_column]
    return [buckets[k] for k in order]
