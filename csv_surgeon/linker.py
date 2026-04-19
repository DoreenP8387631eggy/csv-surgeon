"""linker.py — cross-reference rows from two streams by a shared key column."""
from typing import Iterator, Dict, List, Optional


def _index(rows: Iterator[Dict], key: str) -> Dict[str, List[Dict]]:
    index: Dict[str, List[Dict]] = {}
    for row in rows:
        k = row.get(key, "")
        index.setdefault(k, []).append(row)
    return index


def link_column(
    left_rows: Iterator[Dict],
    right_rows: Iterator[Dict],
    left_key: str,
    right_key: str,
    output_col: str,
    right_col: str,
    default: str = "",
    separator: str = "|",
) -> Iterator[Dict]:
    """Attach values from right_col (right stream) to each left row via key lookup."""
    index = _index(right_rows, right_key)
    for row in left_rows:
        k = row.get(left_key, "")
        matches = index.get(k, [])
        values = [m.get(right_col, "") for m in matches if m.get(right_col, "")]
        out = {**row, output_col: separator.join(values) if values else default}
        yield out


def link_exists(
    left_rows: Iterator[Dict],
    right_rows: Iterator[Dict],
    left_key: str,
    right_key: str,
    output_col: str = "linked",
    true_value: str = "true",
    false_value: str = "false",
) -> Iterator[Dict]:
    """Mark each left row with whether its key exists in the right stream."""
    index = _index(right_rows, right_key)
    for row in left_rows:
        k = row.get(left_key, "")
        flag = true_value if k in index else false_value
        yield {**row, output_col: flag}


def link_count(
    left_rows: Iterator[Dict],
    right_rows: Iterator[Dict],
    left_key: str,
    right_key: str,
    output_col: str = "link_count",
) -> Iterator[Dict]:
    """Attach the count of matching right rows to each left row."""
    index = _index(right_rows, right_key)
    for row in left_rows:
        k = row.get(left_key, "")
        count = len(index.get(k, []))
        yield {**row, output_col: str(count)}
