"""Column value stemming and word-root extraction utilities."""
from __future__ import annotations
from typing import Iterator, Callable
import re


def _simple_stem(word: str) -> str:
    """Minimal suffix-stripping stemmer (Porter-lite)."""
    word = word.lower()
    for suffix in ("tion", "ing", "ness", "ment", "ful", "less", "able", "ible", "ly", "ed", "er", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def stem_column(
    rows: Iterator[dict],
    column: str,
    *,
    out_col: str | None = None,
    stemmer: Callable[[str], str] | None = None,
) -> Iterator[dict]:
    """Stem every whitespace-separated word in *column* and write the result.

    Args:
        rows: input row stream.
        column: column whose value will be stemmed.
        out_col: destination column; defaults to *column* (in-place).
        stemmer: custom stem function; defaults to the built-in suffix stripper.
    """
    fn = stemmer or _simple_stem
    dest = out_col or column

    def _transform(row: dict) -> dict:
        r = dict(row)
        if column not in r:
            return r
        words = re.split(r"(\s+)", r[column])
        r[dest] = "".join(fn(tok) if tok.strip() else tok for tok in words)
        return r

    return (_transform(row) for row in rows)


def unique_stems(
    rows: Iterator[dict],
    column: str,
    *,
    out_col: str = "stems",
    stemmer: Callable[[str], str] | None = None,
    separator: str = " ",
) -> Iterator[dict]:
    """Extract the unique stems from *column* words and store as a joined string."""
    fn = stemmer or _simple_stem

    def _transform(row: dict) -> dict:
        r = dict(row)
        if column not in r:
            return r
        words = re.findall(r"[A-Za-z]+", r[column])
        seen: list[str] = []
        for w in words:
            s = fn(w)
            if s not in seen:
                seen.append(s)
        r[out_col] = separator.join(seen)
        return r

    return (_transform(row) for row in rows)
