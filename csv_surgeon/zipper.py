"""Zip/unzip columns: combine two columns into one or split one into two."""
from typing import Iterator, Dict, Callable


def zip_columns(
    rows: Iterator[Dict],
    col_a: str,
    col_b: str,
    output_col: str,
    separator: str = "|",
    drop_originals: bool = False,
) -> Iterator[Dict]:
    """Combine two columns into one using a separator."""
    for row in rows:
        out = dict(row)
        val_a = out.get(col_a, "")
        val_b = out.get(col_b, "")
        out[output_col] = f"{val_a}{separator}{val_b}"
        if drop_originals:
            out.pop(col_a, None)
            out.pop(col_b, None)
        yield out


def unzip_column(
    rows: Iterator[Dict],
    col: str,
    output_cols: list,
    separator: str = "|",
    drop_original: bool = False,
) -> Iterator[Dict]:
    """Split one column into multiple columns using a separator."""
    n = len(output_cols)
    for row in rows:
        out = dict(row)
        value = out.get(col, "")
        parts = value.split(separator, maxsplit=n - 1)
        # Pad with empty strings if not enough parts
        while len(parts) < n:
            parts.append("")
        for name, part in zip(output_cols, parts):
            out[name] = part
        if drop_original:
            out.pop(col, None)
        yield out


def zip_with(
    rows: Iterator[Dict],
    col_a: str,
    col_b: str,
    output_col: str,
    fn: Callable[[str, str], str],
    drop_originals: bool = False,
) -> Iterator[Dict]:
    """Combine two columns using a custom function."""
    for row in rows:
        out = dict(row)
        val_a = out.get(col_a, "")
        val_b = out.get(col_b, "")
        out[output_col] = fn(val_a, val_b)
        if drop_originals:
            out.pop(col_a, None)
            out.pop(col_b, None)
        yield out
