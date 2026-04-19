"""Numeric scaling and normalization transforms for CSV columns."""
from typing import Iterator, Optional


def _to_float(val: str) -> Optional[float]:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def minmax_scale(rows: Iterator[dict], column: str, out_col: Optional[str] = None,
                 feature_range: tuple = (0.0, 1.0)) -> Iterator[dict]:
    """Scale column values to [min, max] range using min-max normalization."""
    data = list(rows)
    values = [_to_float(r.get(column, "")) for r in data]
    nums = [v for v in values if v is not None]
    if not nums:
        yield from data
        return
    col_min, col_max = min(nums), max(nums)
    rng = col_max - col_min or 1.0
    lo, hi = feature_range
    target = out_col or column
    for row, val in zip(data, values):
        result = dict(row)
        if val is not None:
            scaled = lo + (val - col_min) / rng * (hi - lo)
            result[target] = f"{scaled:.6g}"
        else:
            result[target] = ""
        yield result


def zscore_scale(rows: Iterator[dict], column: str, out_col: Optional[str] = None) -> Iterator[dict]:
    """Standardize column values using z-score (mean=0, std=1)."""
    data = list(rows)
    values = [_to_float(r.get(column, "")) for r in data]
    nums = [v for v in values if v is not None]
    if not nums:
        yield from data
        return
    mean = sum(nums) / len(nums)
    variance = sum((v - mean) ** 2 for v in nums) / len(nums)
    std = variance ** 0.5 or 1.0
    target = out_col or column
    for row, val in zip(data, values):
        result = dict(row)
        result[target] = f"{(val - mean) / std:.6g}" if val is not None else ""
        yield result


def robust_scale(rows: Iterator[dict], column: str, out_col: Optional[str] = None) -> Iterator[dict]:
    """Scale using median and IQR, robust to outliers."""
    data = list(rows)
    values = [_to_float(r.get(column, "")) for r in data]
    nums = sorted(v for v in values if v is not None)
    if not nums:
        yield from data
        return
    n = len(nums)
    median = nums[n // 2] if n % 2 else (nums[n // 2 - 1] + nums[n // 2]) / 2
    q1 = nums[n // 4]
    q3 = nums[(3 * n) // 4]
    iqr = (q3 - q1) or 1.0
    target = out_col or column
    for row, val in zip(data, values):
        result = dict(row)
        result[target] = f"{(val - median) / iqr:.6g}" if val is not None else ""
        yield result
