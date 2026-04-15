"""Column enrichment: compute new columns from existing ones."""

from typing import Callable, Iterable, Iterator


def derive_column(
    column: str,
    expression: Callable[[dict], str],
    overwrite: bool = False,
) -> Callable[[Iterable[dict]], Iterator[dict]]:
    """Add a new column whose value is derived by calling *expression* on each row.

    Args:
        column: Name of the new (or existing) column to write.
        expression: A callable that receives the row dict and returns a string value.
        overwrite: If False (default) and *column* already exists, the row is
                   passed through unchanged.
    """
    def _transform(rows: Iterable[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row and not overwrite:
                yield row
                continue
            try:
                value = expression(row)
            except Exception:
                value = ""
            yield {**row, column: value}

    return _transform


def combine_columns(
    column: str,
    sources: list[str],
    separator: str = " ",
    overwrite: bool = False,
) -> Callable[[Iterable[dict]], Iterator[dict]]:
    """Concatenate *sources* columns into a new *column* separated by *separator*."""
    def _transform(rows: Iterable[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row and not overwrite:
                yield row
                continue
            parts = [row.get(src, "") for src in sources]
            yield {**row, column: separator.join(parts)}

    return _transform


def conditional_column(
    column: str,
    condition: Callable[[dict], bool],
    true_value: str,
    false_value: str = "",
    overwrite: bool = False,
) -> Callable[[Iterable[dict]], Iterator[dict]]:
    """Set *column* to *true_value* when *condition* holds, else *false_value*."""
    def _transform(rows: Iterable[dict]) -> Iterator[dict]:
        for row in rows:
            if column in row and not overwrite:
                yield row
                continue
            try:
                value = true_value if condition(row) else false_value
            except Exception:
                value = false_value
            yield {**row, column: value}

    return _transform
