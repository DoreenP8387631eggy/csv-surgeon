"""cutter.py – slice a column's string value by character position."""
from __future__ import annotations

from typing import Generator, Iterable


Row = dict[str, str]


def _transform(rows: Iterable[Row], col: str, fn) -> Generator[Row, None, None]:
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[col] = fn(row[col])
        yield out


def cut_chars(rows: Iterable[Row], col: str, start: int, end: int | None = None,
              out_col: str | None = None) -> Generator[Row, None, None]:
    """Keep characters from *start* up to (not including) *end*."""
    target = out_col or col
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[target] = row[col][start:end]
        yield out


def cut_before(rows: Iterable[Row], col: str, sep: str,
               out_col: str | None = None) -> Generator[Row, None, None]:
    """Keep the part of the value *before* the first occurrence of *sep*."""
    target = out_col or col
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        value = row[col]
        idx = value.find(sep)
        out[target] = value[:idx] if idx != -1 else value
        yield out


def cut_after(rows: Iterable[Row], col: str, sep: str,
              out_col: str | None = None) -> Generator[Row, None, None]:
    """Keep the part of the value *after* the first occurrence of *sep*."""
    target = out_col or col
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        value = row[col]
        idx = value.find(sep)
        out[target] = value[idx + len(sep):] if idx != -1 else value
        yield out


def cut_words(rows: Iterable[Row], col: str, start: int, end: int | None = None,
              sep: str = " ", out_col: str | None = None) -> Generator[Row, None, None]:
    """Keep words from *start* up to (not including) *end* (whitespace-split)."""
    target = out_col or col
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        words = row[col].split(sep)
        out[target] = sep.join(words[start:end])
        yield out
