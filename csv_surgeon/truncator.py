"""Truncate or pad string values in CSV columns to a fixed width."""

from typing import Iterator, Dict, Optional


def truncate_column(
    column: str,
    max_length: int,
    suffix: str = "",
) -> callable:
    """Return a transform that truncates values in *column* to *max_length* chars.

    If *suffix* is provided (e.g. "…") it is appended after truncation so the
    total length stays within *max_length*.
    """
    if max_length < len(suffix):
        raise ValueError(
            f"max_length ({max_length}) must be >= len(suffix) ({len(suffix)})"
        )

    effective = max_length - len(suffix)

    def _transform(
        rows: Iterator[Dict[str, str]]
    ) -> Iterator[Dict[str, str]]:
        for row in rows:
            if column in row:
                val = row[column]
                if len(val) > max_length:
                    row = {**row, column: val[:effective] + suffix}
            yield row

    return _transform


def pad_column(
    column: str,
    width: int,
    fill_char: str = " ",
    align: str = "left",
) -> callable:
    """Return a transform that pads values in *column* to exactly *width* chars.

    *align* must be one of ``'left'``, ``'right'``, or ``'center'``.
    Values already longer than *width* are left unchanged.
    """
    if len(fill_char) != 1:
        raise ValueError("fill_char must be a single character")
    if align not in ("left", "right", "center"):
        raise ValueError("align must be 'left', 'right', or 'center'")

    def _transform(
        rows: Iterator[Dict[str, str]]
    ) -> Iterator[Dict[str, str]]:
        for row in rows:
            if column in row:
                val = row[column]
                if align == "left":
                    padded = val.ljust(width, fill_char)
                elif align == "right":
                    padded = val.rjust(width, fill_char)
                else:
                    padded = val.center(width, fill_char)
                row = {**row, column: padded}
            yield row

    return _transform
