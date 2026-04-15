"""CLI integration for the sampler feature.

Exposes the `cmd_sample` function consumed by csv_surgeon/cli.py.
"""

import sys
from typing import Optional

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.sampler import (
    sample_first_n,
    sample_random,
    sample_every_nth,
    sample_percentage,
)


def cmd_sample(
    input_path: str,
    output_path: str,
    mode: str,
    n: Optional[int] = None,
    pct: Optional[float] = None,
    nth: Optional[int] = None,
    offset: int = 0,
    seed: Optional[int] = None,
) -> None:
    """Sample rows from a CSV file and write results to output.

    Args:
        input_path:  Path to the source CSV file.
        output_path: Path for the output CSV file ('-' for stdout).
        mode:        Sampling strategy — one of 'first', 'random', 'nth', 'pct'.
        n:           Number of rows (required for 'first' and 'random' modes).
        pct:         Percentage of rows to keep (required for 'pct' mode).
        nth:         Step size for 'nth' mode.
        offset:      Row offset for 'nth' mode (default 0).
        seed:        Random seed for reproducible sampling.
    """
    reader = StreamingCSVReader(input_path)
    row_iter = reader.iter_rows()

    if mode == "first":
        if n is None:
            raise ValueError("'first' mode requires --n")
        sampled = iter(sample_first_n(row_iter, n))

    elif mode == "random":
        if n is None:
            raise ValueError("'random' mode requires --n")
        sampled = iter(sample_random(row_iter, n, seed=seed))

    elif mode == "nth":
        if nth is None:
            raise ValueError("'nth' mode requires --nth")
        sampled = sample_every_nth(row_iter, nth, offset=offset)

    elif mode == "pct":
        if pct is None:
            raise ValueError("'pct' mode requires --pct")
        sampled = sample_percentage(row_iter, pct, seed=seed)

    else:
        raise ValueError(f"Unknown sampling mode: {mode!r}")

    if output_path == "-":
        import io
        sink = io.TextIOWrapper(sys.stdout.buffer, newline="")
        writer = StreamingCSVWriter(sink)
    else:
        writer = StreamingCSVWriter(output_path)

    headers = reader.headers or []
    writer.write_rows(sampled, headers=headers)
