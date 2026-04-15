"""Column value replacement and substitution transforms."""

import re
from typing import Dict, Iterator, Optional


def replace_value(
    column: str,
    old_value: str,
    new_value: str,
    case_sensitive: bool = True,
) -> callable:
    """Replace exact matches of old_value with new_value in the given column."""

    def _transform(rows: Iterator[Dict]) -> Iterator[Dict]:
        for row in rows:
            if column not in row:
                yield row
                continue
            current = row[column]
            if case_sensitive:
                row[column] = new_value if current == old_value else current
            else:
                row[column] = new_value if current.lower() == old_value.lower() else current
            yield row

    return _transform


def replace_pattern(
    column: str,
    pattern: str,
    replacement: str,
    flags: int = 0,
) -> callable:
    """Replace regex pattern matches in the given column with replacement."""
    compiled = re.compile(pattern, flags)

    def _transform(rows: Iterator[Dict]) -> Iterator[Dict]:
        for row in rows:
            if column not in row:
                yield row
                continue
            row[column] = compiled.sub(replacement, row[column])
            yield row

    return _transform


def replace_map(
    column: str,
    mapping: Dict[str, str],
    default: Optional[str] = None,
) -> callable:
    """Replace values in column using a lookup mapping.

    If a value is not in the mapping, it is left unchanged unless
    ``default`` is provided, in which case the default is used.
    """

    def _transform(rows: Iterator[Dict]) -> Iterator[Dict]:
        for row in rows:
            if column not in row:
                yield row
                continue
            current = row[column]
            if current in mapping:
                row[column] = mapping[current]
            elif default is not None:
                row[column] = default
            yield row

    return _transform
