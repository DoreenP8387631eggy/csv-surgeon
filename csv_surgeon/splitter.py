"""Split a CSV stream into chunks by row count or column value."""

from typing import Iterator, Dict, List, Optional


def split_by_count(
    rows: Iterator[Dict[str, str]], chunk_size: int
) -> Iterator[List[Dict[str, str]]]:
    """Yield successive chunks of up to `chunk_size` rows.

    Args:
        rows: An iterator of row dicts.
        chunk_size: Maximum number of rows per chunk.

    Yields:
        Lists of row dicts, each of length <= chunk_size.

    Raises:
        ValueError: If chunk_size is less than 1.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")

    chunk: List[Dict[str, str]] = []
    for row in rows:
        chunk.append(row)
        if len(chunk) == chunk_size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def split_by_column(
    rows: Iterator[Dict[str, str]], column: str
) -> Iterator[tuple]:
    """Group consecutive rows that share the same value in `column`.

    Rows do NOT need to be pre-sorted; a new group is emitted whenever
    the column value changes (similar to Unix `uniq`).

    Args:
        rows: An iterator of row dicts.
        column: The column name to split on.

    Yields:
        Tuples of (group_value, list_of_rows).

    Raises:
        KeyError: If `column` is missing from a row.
    """
    current_value: Optional[str] = None
    group: List[Dict[str, str]] = []
    started = False

    for row in rows:
        value = row[column]  # intentional KeyError on missing column
        if not started:
            current_value = value
            started = True

        if value != current_value:
            yield (current_value, group)
            current_value = value
            group = []

        group.append(row)

    if group:
        yield (current_value, group)
