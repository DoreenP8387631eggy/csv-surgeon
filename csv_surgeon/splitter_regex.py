"""Split CSV rows into multiple rows based on a regex pattern match in a column."""
import re
from typing import Iterator, Dict, Optional


def split_on_pattern(
    rows: Iterator[Dict[str, str]],
    column: str,
    pattern: str,
    output_column: Optional[str] = None,
    flags: int = 0,
) -> Iterator[Dict[str, str]]:
    """Yield one row per regex match in `column`. Non-matching rows are passed through."""
    out_col = output_column or column
    compiled = re.compile(pattern, flags)
    for row in rows:
        value = row.get(column, "")
        matches = compiled.findall(value)
        if not matches:
            yield dict(row)
        else:
            for match in matches:
                new_row = dict(row)
                new_row[out_col] = match if isinstance(match, str) else "".join(match)
                yield new_row


def split_on_delimiter(
    rows: Iterator[Dict[str, str]],
    column: str,
    delimiter: str = ",",
    output_column: Optional[str] = None,
    strip: bool = True,
) -> Iterator[Dict[str, str]]:
    """Yield one row per delimited segment in `column`."""
    out_col = output_column or column
    for row in rows:
        value = row.get(column, "")
        parts = value.split(delimiter)
        if len(parts) <= 1:
            yield dict(row)
        else:
            for part in parts:
                new_row = dict(row)
                new_row[out_col] = part.strip() if strip else part
                yield new_row


def split_keep_original(
    rows: Iterator[Dict[str, str]],
    column: str,
    pattern: str,
    output_column: str,
    flags: int = 0,
) -> Iterator[Dict[str, str]]:
    """Like split_on_pattern but always writes to output_column, preserving original column."""
    compiled = re.compile(pattern, flags)
    for row in rows:
        value = row.get(column, "")
        matches = compiled.findall(value)
        if not matches:
            new_row = dict(row)
            new_row[output_column] = ""
            yield new_row
        else:
            for match in matches:
                new_row = dict(row)
                new_row[output_column] = match if isinstance(match, str) else "".join(match)
                yield new_row
