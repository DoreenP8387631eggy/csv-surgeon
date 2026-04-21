"""combiner.py – merge multiple column values into a new column using a template or separator."""

from typing import Iterable, Iterator, Callable, Optional


def combine_template(
    rows: Iterable[dict],
    template: str,
    output_col: str = "combined",
    default: str = "",
) -> Iterator[dict]:
    """Render *template* with each row's values and store in *output_col*.

    Example template: "{first_name} {last_name}".
    Missing keys are replaced with *default*.
    """
    for row in rows:
        try:
            value = template.format_map(_DefaultDict(row, default))
        except Exception:
            value = default
        out = dict(row)
        out[output_col] = value
        yield out


def combine_columns(
    rows: Iterable[dict],
    columns: list,
    output_col: str = "combined",
    separator: str = " ",
    skip_empty: bool = True,
) -> Iterator[dict]:
    """Concatenate *columns* values with *separator* into *output_col*.

    If *skip_empty* is True, blank values are omitted from the result.
    """
    for row in rows:
        parts = [row.get(c, "") for c in columns]
        if skip_empty:
            parts = [p for p in parts if p.strip()]
        out = dict(row)
        out[output_col] = separator.join(parts)
        yield out


def combine_with(
    rows: Iterable[dict],
    columns: list,
    fn: Callable[[list], str],
    output_col: str = "combined",
) -> Iterator[dict]:
    """Apply *fn* to the list of values from *columns* and store result in *output_col*."""
    for row in rows:
        values = [row.get(c, "") for c in columns]
        out = dict(row)
        out[output_col] = fn(values)
        yield out


class _DefaultDict(dict):
    """dict subclass that returns *default* for missing keys during format_map."""

    def __init__(self, data: dict, default: str = ""):
        super().__init__(data)
        self._default = default

    def __missing__(self, key: str) -> str:  # type: ignore[override]
        return self._default
