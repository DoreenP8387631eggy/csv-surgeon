"""Fuzzy deduplication using similarity thresholds."""
from __future__ import annotations
from typing import Iterator, Iterable


def _similarity(a: str, b: str) -> float:
    """Simple character-level Jaccard similarity."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    set_a = set(a.lower())
    set_b = set(b.lower())
    intersection = len(set_a & set_b)
    union = len(set_a | set_b)
    return intersection / union if union else 0.0


def _row_signature(row: dict, columns: list[str]) -> str:
    return " ".join(row.get(c, "") for c in columns)


def fuzzy_deduplicate(
    rows: Iterable[dict],
    columns: list[str],
    threshold: float = 0.85,
) -> Iterator[dict]:
    """Yield rows, skipping those too similar to an already-seen row.

    Compares the concatenated values of *columns* using Jaccard similarity.
    Rows whose similarity to any retained row exceeds *threshold* are dropped.
    """
    seen: list[str] = []
    for row in rows:
        sig = _row_signature(row, columns)
        if any(_similarity(sig, s) >= threshold for s in seen):
            continue
        seen.append(sig)
        yield row


def fuzzy_deduplicate_sorted(
    rows: Iterable[dict],
    columns: list[str],
    threshold: float = 0.85,
) -> Iterator[dict]:
    """Streaming fuzzy dedup that only compares against the previous row.

    Suitable for pre-sorted streams where near-duplicates are adjacent.
    Much more memory-efficient than fuzzy_deduplicate for large datasets.
    """
    prev_sig: str | None = None
    for row in rows:
        sig = _row_signature(row, columns)
        if prev_sig is not None and _similarity(sig, prev_sig) >= threshold:
            continue
        prev_sig = sig
        yield row
