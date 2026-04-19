"""Generate sequential or patterned values for CSV rows."""
from typing import Iterator, Dict, Callable, Optional
import itertools


def sequence_column(
    rows: Iterator[Dict],
    col: str,
    start: int = 1,
    step: int = 1,
    overwrite: bool = False,
) -> Iterator[Dict]:
    """Add or overwrite a column with an incrementing integer sequence."""
    counter = itertools.count(start, step)
    for row in rows:
        if overwrite or col not in row or row[col] == "":
            yield {**row, col: str(next(counter))}
        else:
            next(counter)  # keep counter in sync
            yield row


def alpha_sequence_column(
    rows: Iterator[Dict],
    col: str,
    prefix: str = "",
    start: int = 1,
    step: int = 1,
    pad: int = 0,
) -> Iterator[Dict]:
    """Add a column with a prefixed, optionally zero-padded sequence."""
    counter = itertools.count(start, step)
    for row in rows:
        val = next(counter)
        formatted = f"{prefix}{str(val).zfill(pad)}"
        yield {**row, col: formatted}


def cycle_column(
    rows: Iterator[Dict],
    col: str,
    values: list,
) -> Iterator[Dict]:
    """Cycle through a list of values, assigning one per row."""
    if not values:
        for row in rows:
            yield {**row, col: ""}
        return
    cycler = itertools.cycle(values)
    for row in rows:
        yield {**row, col: str(next(cycler))}


def repeat_column(
    rows: Iterator[Dict],
    col: str,
    value: str,
    overwrite: bool = True,
) -> Iterator[Dict]:
    """Fill a column with a constant value."""
    for row in rows:
        if overwrite or col not in row or row[col] == "":
            yield {**row, col: value}
        else:
            yield row
