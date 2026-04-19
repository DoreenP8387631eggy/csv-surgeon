"""Annotate rows with metadata such as row number, source tag, or hash."""
import hashlib
from typing import Iterable, Iterator


def annotate_row_number(
    rows: Iterable[dict],
    output_col: str = "_row_num",
    start: int = 1,
) -> Iterator[dict]:
    """Add a sequential row number to each row."""
    for i, row in enumerate(rows, start=start):
        yield {**row, output_col: str(i)}


def annotate_source(
    rows: Iterable[dict],
    source: str,
    output_col: str = "_source",
) -> Iterator[dict]:
    """Tag every row with a fixed source label."""
    for row in rows:
        yield {**row, output_col: source}


def annotate_hash(
    rows: Iterable[dict],
    columns: list[str] | None = None,
    output_col: str = "_hash",
    algorithm: str = "md5",
) -> Iterator[dict]:
    """Add a hash of selected (or all) column values to each row."""
    for row in rows:
        keys = columns if columns is not None else sorted(row.keys())
        raw = "|".join(str(row.get(k, "")) for k in keys)
        digest = hashlib.new(algorithm, raw.encode()).hexdigest()
        yield {**row, output_col: digest}


def annotate_is_empty(
    rows: Iterable[dict],
    column: str,
    output_col: str = "_is_empty",
) -> Iterator[dict]:
    """Flag whether a column value is empty/blank."""
    for row in rows:
        val = row.get(column, "")
        yield {**row, output_col: "true" if not val or not val.strip() else "false"}
