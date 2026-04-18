"""Column reordering and selection utilities."""
from typing import Iterator, List, Dict


def reorder_columns(rows: Iterator[Dict], order: List[str]) -> Iterator[Dict]:
    """Yield rows with columns reordered. Missing columns get empty string."""
    for row in rows:
        yield {col: row.get(col, "") for col in order}


def select_columns(rows: Iterator[Dict], columns: List[str]) -> Iterator[Dict]:
    """Yield rows containing only the specified columns."""
    for row in rows:
        yield {col: row.get(col, "") for col in columns if col in row or True}


def drop_columns(rows: Iterator[Dict], columns: List[str]) -> Iterator[Dict]:
    """Yield rows with specified columns removed."""
    drop_set = set(columns)
    for row in rows:
        yield {k: v for k, v in row.items() if k not in drop_set}


def move_column_first(rows: Iterator[Dict], column: str) -> Iterator[Dict]:
    """Yield rows with the specified column moved to the front."""
    for row in rows:
        if column not in row:
            yield row
            continue
        reordered = {column: row[column]}
        reordered.update({k: v for k, v in row.items() if k != column})
        yield reordered


def move_column_last(rows: Iterator[Dict], column: str) -> Iterator[Dict]:
    """Yield rows with the specified column moved to the end."""
    for row in rows:
        if column not in row:
            yield row
            continue
        reordered = {k: v for k, v in row.items() if k != column}
        reordered[column] = row[column]
        yield reordered
