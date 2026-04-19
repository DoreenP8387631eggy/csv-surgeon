"""clipper.py – clamp and clip numeric column values to a defined range."""
from typing import Iterator, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def clamp_column(
    rows: Iterator[dict],
    column: str,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    output_column: Optional[str] = None,
) -> Iterator[dict]:
    """Clamp values in *column* to [min_value, max_value]. Non-numeric rows pass through unchanged."""
    out_col = output_column or column
    for row in rows:
        result = dict(row)
        if column not in row:
            yield result
            continue
        val = _to_float(row[column])
        if val is None:
            yield result
            continue
        if min_value is not None:
            val = max(min_value, val)
        if max_value is not None:
            val = min(max_value, val)
        result[out_col] = str(val) if val != int(val) else str(int(val))
        yield result


def clip_below(
    rows: Iterator[dict],
    column: str,
    threshold: float,
    replacement: str = "",
    output_column: Optional[str] = None,
) -> Iterator[dict]:
    """Replace values below *threshold* with *replacement*."""
    out_col = output_column or column
    for row in rows:
        result = dict(row)
        if column not in row:
            yield result
            continue
        val = _to_float(row[column])
        if val is not None and val < threshold:
            result[out_col] = replacement
        yield result


def clip_above(
    rows: Iterator[dict],
    column: str,
    threshold: float,
    replacement: str = "",
    output_column: Optional[str] = None,
) -> Iterator[dict]:
    """Replace values above *threshold* with *replacement*."""
    out_col = output_column or column
    for row in rows:
        result = dict(row)
        if column not in row:
            yield result
            continue
        val = _to_float(row[column])
        if val is not None and val > threshold:
            result[out_col] = replacement
        yield result
