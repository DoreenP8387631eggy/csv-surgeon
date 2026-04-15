"""Row sampling utilities for large CSV streams."""

import random
from typing import Iterator, List, Optional


def sample_first_n(rows: Iterator[dict], n: int) -> List[dict]:
    """Return the first n rows from the stream."""
    result = []
    for row in rows:
        if len(result) >= n:
            break
        result.append(row)
    return result


def sample_random(rows: Iterator[dict], n: int, seed: Optional[int] = None) -> List[dict]:
    """Return a random sample of n rows using reservoir sampling.

    Memory-efficient: only holds n rows at a time regardless of input size.
    """
    rng = random.Random(seed)
    reservoir: List[dict] = []

    for i, row in enumerate(rows):
        if i < n:
            reservoir.append(row)
        else:
            j = rng.randint(0, i)
            if j < n:
                reservoir[j] = row

    return reservoir


def sample_every_nth(rows: Iterator[dict], n: int, offset: int = 0) -> Iterator[dict]:
    """Yield every nth row from the stream, starting at the given offset.

    Args:
        rows: Input row iterator.
        n: Step size — yield one row every n rows.
        offset: Index of the first row to yield (0-based).
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if offset < 0 or offset >= n:
        raise ValueError("offset must be in range [0, n)")

    for i, row in enumerate(rows):
        if i % n == offset:
            yield row


def sample_percentage(rows: Iterator[dict], pct: float, seed: Optional[int] = None) -> Iterator[dict]:
    """Yield each row with probability pct/100.

    Args:
        rows: Input row iterator.
        pct: Percentage of rows to keep (0 < pct <= 100).
        seed: Optional random seed for reproducibility.
    """
    if not (0 < pct <= 100):
        raise ValueError("pct must be in range (0, 100]")

    rng = random.Random(seed)
    threshold = pct / 100.0

    for row in rows:
        if rng.random() < threshold:
            yield row
