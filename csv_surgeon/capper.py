"""Column value capper: limit the number of words or characters in a field."""
from typing import Iterator, Optional


def _transform(rows: Iterator[dict], col: str, fn) -> Iterator[dict]:
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[col] = fn(row[col])
        yield out


def cap_words(rows: Iterator[dict], col: str, max_words: int,
              sep: str = " ", out_col: Optional[str] = None) -> Iterator[dict]:
    """Keep only the first *max_words* whitespace-separated words."""
    target = out_col or col

    def fn(value: str) -> str:
        words = value.split()
        return sep.join(words[:max_words])

    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[target] = fn(row[col])
        yield out


def cap_chars(rows: Iterator[dict], col: str, max_chars: int,
              ellipsis: str = "", out_col: Optional[str] = None) -> Iterator[dict]:
    """Keep only the first *max_chars* characters, appending *ellipsis* if truncated."""
    target = out_col or col

    def fn(value: str) -> str:
        if len(value) <= max_chars:
            return value
        keep = max_chars - len(ellipsis)
        if keep < 0:
            keep = 0
        return value[:keep] + ellipsis

    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[target] = fn(row[col])
        yield out


def cap_sentences(rows: Iterator[dict], col: str, max_sentences: int,
                  out_col: Optional[str] = None) -> Iterator[dict]:
    """Keep only the first *max_sentences* sentences (split on '.')."""
    import re
    target = out_col or col

    def fn(value: str) -> str:
        parts = re.split(r'(?<=[.!?])\s+', value.strip())
        kept = parts[:max_sentences]
        return " ".join(kept)

    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[target] = fn(row[col])
        yield out
