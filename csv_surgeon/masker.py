"""Column masking/redaction utilities for sensitive data."""

import re
from typing import Callable, Iterator


def mask_column(column: str, mask_char: str = "*", keep_last: int = 0) -> Callable:
    """Mask all or part of a column's value with a mask character.

    Args:
        column: Column name to mask.
        mask_char: Character to use for masking (default '*').
        keep_last: Number of trailing characters to keep visible.
    """
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column not in row:
                yield row
                continue
            value = row[column]
            if not value:
                yield row
                continue
            if keep_last > 0 and len(value) > keep_last:
                masked = mask_char * (len(value) - keep_last) + value[-keep_last:]
            else:
                masked = mask_char * len(value)
            yield {**row, column: masked}
    return _transform


def redact_column(column: str, replacement: str = "[REDACTED]") -> Callable:
    """Replace a column's entire value with a fixed replacement string."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column not in row:
                yield row
                continue
            yield {**row, column: replacement}
    return _transform


def mask_pattern(column: str, pattern: str, mask_char: str = "*") -> Callable:
    """Mask substrings matching a regex pattern within a column's value.

    The matched portion is replaced with mask_char repeated to the same length.
    """
    compiled = re.compile(pattern)

    def _replace(match: re.Match) -> str:
        return mask_char * len(match.group(0))

    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        for row in rows:
            if column not in row:
                yield row
                continue
            value = row[column]
            yield {**row, column: compiled.sub(_replace, value)}
    return _transform
