"""censor.py – redact or obscure values matching a pattern or column list."""
from __future__ import annotations

import re
from typing import Iterable, Iterator


def _transform(rows: Iterable[dict], col: str, fn) -> Iterator[dict]:
    for row in rows:
        out = dict(row)
        if col in out:
            out[col] = fn(out[col])
        yield out


def censor_column(rows: Iterable[dict], col: str, replacement: str = "***") -> Iterator[dict]:
    """Replace every value in *col* with *replacement*."""
    return _transform(rows, col, lambda _: replacement)


def censor_pattern(
    rows: Iterable[dict],
    col: str,
    pattern: str,
    replacement: str = "***",
    flags: int = 0,
) -> Iterator[dict]:
    """Replace substrings in *col* that match *pattern* with *replacement*."""
    rx = re.compile(pattern, flags)
    return _transform(rows, col, lambda v: rx.sub(replacement, v))


def censor_columns(
    rows: Iterable[dict], cols: list[str], replacement: str = "***"
) -> Iterator[dict]:
    """Replace values in all listed columns with *replacement*."""
    for row in rows:
        out = dict(row)
        for col in cols:
            if col in out:
                out[col] = replacement
        yield out


def censor_if(
    rows: Iterable[dict],
    col: str,
    predicate,
    replacement: str = "***",
) -> Iterator[dict]:
    """Replace values in *col* with *replacement* when *predicate(value)* is True."""
    return _transform(rows, col, lambda v: replacement if predicate(v) else v)
