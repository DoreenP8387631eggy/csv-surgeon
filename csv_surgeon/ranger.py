"""Row range selection utilities for csv-surgeon."""

from typing import Iterable, Iterator, Dict


def slice_rows(
    rows: Iterable[Dict[str, str]],
    start: int = 0,
    stop: int = None,
    step: int = 1,
) -> Iterator[Dict[str, str]]:
    """Yield rows within [start, stop) with optional step, zero-indexed."""
    if step < 1:
        raise ValueError("step must be >= 1")
    for index, row in enumerate(rows):
        if stop is not None and index >= stop:
            break
        if index < start:
            continue
        if (index - start) % step == 0:
            yield row


def skip_rows(
    rows: Iterable[Dict[str, str]],
    n: int,
) -> Iterator[Dict[str, str]]:
    """Skip the first *n* rows and yield the rest."""
    if n < 0:
        raise ValueError("n must be >= 0")
    for index, row in enumerate(rows):
        if index >= n:
            yield row


def limit_rows(
    rows: Iterable[Dict[str, str]],
    n: int,
) -> Iterator[Dict[str, str]]:
    """Yield at most *n* rows."""
    if n < 0:
        raise ValueError("n must be >= 0")
    for index, row in enumerate(rows):
        if index >= n:
            break
        yield row


def rows_between(
    rows: Iterable[Dict[str, str]],
    start: int,
    stop: int,
) -> Iterator[Dict[str, str]]:
    """Yield rows whose 0-based index satisfies start <= index < stop."""
    if start < 0 or stop < 0:
        raise ValueError("start and stop must be >= 0")
    if stop <= start:
        return
    yield from slice_rows(rows, start=start, stop=stop)
