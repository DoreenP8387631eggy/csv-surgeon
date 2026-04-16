"""Tag rows with labels based on column conditions."""

from typing import Callable, Iterable, Iterator


def tag_column(
    rows: Iterable[dict],
    tag_col: str,
    rules: list[tuple[Callable[[dict], bool], str]],
    default: str = "",
) -> Iterator[dict]:
    """Add a tag column based on the first matching rule."""
    for row in rows:
        label = default
        for predicate, tag in rules:
            if predicate(row):
                label = tag
                break
        yield {**row, tag_col: label}


def tag_multi(
    rows: Iterable[dict],
    tag_col: str,
    rules: list[tuple[Callable[[dict], bool], str]],
    separator: str = "|",
) -> Iterator[dict]:
    """Add a tag column with ALL matching rule labels joined by separator."""
    for row in rows:
        labels = [tag for predicate, tag in rules if predicate(row)]
        yield {**row, tag_col: separator.join(labels)}


def tag_equals(
    column: str, value: str, tag: str
) -> tuple[Callable[[dict], bool], str]:
    """Rule: tag when column equals value (case-insensitive)."""
    return (lambda row: row.get(column, "").strip().lower() == value.strip().lower(), tag)


def tag_contains(
    column: str, value: str, tag: str
) -> tuple[Callable[[dict], bool], str]:
    """Rule: tag when column contains value."""
    return (lambda row: value.lower() in row.get(column, "").lower(), tag)


def tag_numeric_range(
    column: str, low: float, high: float, tag: str
) -> tuple[Callable[[dict], bool], str]:
    """Rule: tag when numeric column value is within [low, high]."""
    def predicate(row: dict) -> bool:
        try:
            v = float(row.get(column, ""))
            return low <= v <= high
        except (ValueError, TypeError):
            return False
    return predicate, tag
