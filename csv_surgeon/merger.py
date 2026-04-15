"""Vertical merging (stacking) of multiple CSV row streams."""
from typing import Iterable, Iterator, Dict, Any, List, Optional


def merge_rows(
    streams: List[Iterable[Dict[str, Any]]],
    fill_value: str = "",
) -> Iterator[Dict[str, Any]]:
    """Yield rows from multiple streams sequentially.

    Columns present in one stream but missing in another are filled with
    *fill_value* so every output row has the same key set.

    Args:
        streams: Ordered list of row iterables (each yields dicts).
        fill_value: Value used for missing columns (default empty string).

    Yields:
        Merged row dicts with a unified column set.
    """
    if not streams:
        return

    # Collect all column names seen across every stream (preserving first-seen order)
    all_keys: List[str] = []
    seen_keys: set = set()
    buffered: List[List[Dict[str, Any]]] = []

    for stream in streams:
        rows = list(stream)
        buffered.append(rows)
        for row in rows:
            for key in row:
                if key not in seen_keys:
                    all_keys.append(key)
                    seen_keys.add(key)

    for rows in buffered:
        for row in rows:
            yield {key: row.get(key, fill_value) for key in all_keys}


def merge_rows_strict(
    streams: List[Iterable[Dict[str, Any]]],
) -> Iterator[Dict[str, Any]]:
    """Merge streams, raising ValueError if column sets differ.

    Args:
        streams: Ordered list of row iterables.

    Yields:
        Row dicts unchanged.

    Raises:
        ValueError: When a stream contains columns not present in the first stream.
    """
    if not streams:
        return

    reference_keys: Optional[List[str]] = None

    for stream_index, stream in enumerate(streams):
        for row in stream:
            if reference_keys is None:
                reference_keys = list(row.keys())
            elif set(row.keys()) != set(reference_keys):
                raise ValueError(
                    f"Stream {stream_index} has columns {sorted(row.keys())} "
                    f"but expected {sorted(reference_keys)}"
                )
            yield row
