"""Flattener: expand multi-value cells into multiple rows or join nested dicts."""
from typing import Iterator, Dict, Any, List, Optional


def flatten_column(
    rows: Iterator[Dict[str, Any]],
    column: str,
    delimiter: str = "|",
    strip: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Expand a delimited cell into one row per value.

    Each output row is a copy of the original with *column* replaced by a
    single token.  Rows where the column is absent or empty are passed through
    unchanged.

    Args:
        rows:      Source row iterator.
        column:    Name of the column to expand.
        delimiter: Delimiter used to split the cell value.
        strip:     Whether to strip whitespace from each token.
    """
    for row in rows:
        value = row.get(column, "")
        if not value:
            yield row
            continue
        tokens: List[str] = value.split(delimiter)
        if strip:
            tokens = [t.strip() for t in tokens]
        tokens = [t for t in tokens if t]  # drop empty tokens
        if not tokens:
            yield row
            continue
        for token in tokens:
            new_row = dict(row)
            new_row[column] = token
            yield new_row


def flatten_prefix(
    rows: Iterator[Dict[str, Any]],
    prefix: str,
    separator: str = "_",
    keep_original: bool = False,
) -> Iterator[Dict[str, Any]]:
    """Promote columns that share a common prefix into a new flat namespace.

    Columns matching *prefix + separator + suffix* are renamed to just *suffix*.
    Other columns are preserved.  If *keep_original* is True the original
    prefixed columns are also retained.

    Args:
        rows:          Source row iterator.
        prefix:        Prefix to strip (without the separator).
        separator:     Separator between prefix and the rest of the key.
        keep_original: If True, also keep the original prefixed column.
    """
    match = prefix + separator
    for row in rows:
        new_row: Dict[str, Any] = {}
        for key, value in row.items():
            if key.startswith(match):
                short_key = key[len(match):]
                new_row[short_key] = value
                if keep_original:
                    new_row[key] = value
            else:
                new_row[key] = value
        yield new_row
