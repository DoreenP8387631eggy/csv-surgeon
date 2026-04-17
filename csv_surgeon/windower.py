"""Windowing utilities: rolling and lag/lead column operations."""
from collections import deque
from typing import Iterator, Dict, Any, Optional, Callable


def rolling_window(
    rows: Iterator[Dict[str, Any]],
    column: str,
    window_size: int,
    output_column: str,
    func: Callable[[list], Any],
    fill: str = "",
) -> Iterator[Dict[str, Any]]:
    """Apply func over a rolling window of `column` values."""
    if window_size < 1:
        raise ValueError("window_size must be >= 1")
    buf: deque = deque(maxlen=window_size)
    for row in rows:
        val = row.get(column, "")
        try:
            buf.append(float(val))
        except (ValueError, TypeError):
            buf.append(None)
        out = dict(row)
        if len(buf) < window_size or any(v is None for v in buf):
            out[output_column] = fill
        else:
            out[output_column] = str(func(list(buf)))
        yield out


def rolling_mean(
    rows: Iterator[Dict[str, Any]],
    column: str,
    window_size: int,
    output_column: Optional[str] = None,
    fill: str = "",
) -> Iterator[Dict[str, Any]]:
    out_col = output_column or f"{column}_rolling_mean"
    return rolling_window(rows, column, window_size, out_col, lambda w: round(sum(w) / len(w), 6), fill)


def rolling_sum(
    rows: Iterator[Dict[str, Any]],
    column: str,
    window_size: int,
    output_column: Optional[str] = None,
    fill: str = "",
) -> Iterator[Dict[str, Any]]:
    out_col = output_column or f"{column}_rolling_sum"
    return rolling_window(rows, column, window_size, out_col, sum, fill)


def lag_column(
    rows: Iterator[Dict[str, Any]],
    column: str,
    periods: int = 1,
    output_column: Optional[str] = None,
    fill: str = "",
) -> Iterator[Dict[str, Any]]:
    """Add a column with the value of `column` from `periods` rows ago."""
    if periods < 1:
        raise ValueError("periods must be >= 1")
    out_col = output_column or f"{column}_lag{periods}"
    buf: deque = deque(maxlen=periods)
    for row in rows:
        out = dict(row)
        out[out_col] = buf[0] if len(buf) == periods else fill
        buf.append(row.get(column, ""))
        yield out


def lead_column(
    rows: Iterator[Dict[str, Any]],
    column: str,
    periods: int = 1,
    output_column: Optional[str] = None,
    fill: str = "",
) -> Iterator[Dict[str, Any]]:
    """Add a column with the value of `column` from `periods` rows ahead."""
    if periods < 1:
        raise ValueError("periods must be >= 1")
    out_col = output_column or f"{column}_lead{periods}"
    buf: deque = deque()
    source = list(rows)
    for i, row in enumerate(source):
        out = dict(row)
        ahead = i + periods
        out[out_col] = source[ahead].get(column, "") if ahead < len(source) else fill
        yield out
