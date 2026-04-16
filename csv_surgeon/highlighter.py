"""Highlight rows or cells matching conditions by adding a marker column."""
from typing import Iterable, Callable, Iterator


def highlight_rows(
    rows: Iterable[dict],
    predicate: Callable[[dict], bool],
    column: str = "_highlight",
    true_value: str = "1",
    false_value: str = "0",
) -> Iterator[dict]:
    """Add a boolean marker column based on a predicate."""
    for row in rows:
        out = dict(row)
        out[column] = true_value if predicate(row) else false_value
        yield out


def highlight_equals(
    rows: Iterable[dict],
    key: str,
    value: str,
    column: str = "_highlight",
    case_sensitive: bool = True,
) -> Iterator[dict]:
    """Highlight rows where key equals value."""
    def predicate(row: dict) -> bool:
        cell = row.get(key, "")
        if case_sensitive:
            return cell == value
        return cell.lower() == value.lower()

    return highlight_rows(rows, predicate, column=column)


def highlight_contains(
    rows: Iterable[dict],
    key: str,
    substring: str,
    column: str = "_highlight",
    case_sensitive: bool = True,
) -> Iterator[dict]:
    """Highlight rows where key contains substring."""
    def predicate(row: dict) -> bool:
        cell = row.get(key, "")
        if case_sensitive:
            return substring in cell
        return substring.lower() in cell.lower()

    return highlight_rows(rows, predicate, column=column)


def highlight_numeric_range(
    rows: Iterable[dict],
    key: str,
    low: float,
    high: float,
    column: str = "_highlight",
) -> Iterator[dict]:
    """Highlight rows where numeric value of key is within [low, high]."""
    def predicate(row: dict) -> bool:
        try:
            v = float(row.get(key, ""))
            return low <= v <= high
        except (ValueError, TypeError):
            return False

    return highlight_rows(rows, predicate, column=column)
