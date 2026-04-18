"""Outlier detection transforms for CSV rows."""
from typing import Iterator, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def flag_zscore(rows: Iterator[dict], column: str, threshold: float = 3.0,
                output_col: str = "is_outlier") -> Iterator[dict]:
    """Buffer all rows, compute z-score per row, yield with outlier flag."""
    buffered = list(rows)
    values = [_to_float(r.get(column, "")) for r in buffered]
    nums = [v for v in values if v is not None]
    if len(nums) < 2:
        for row in buffered:
            yield {**row, output_col: "false"}
        return
    mean = sum(nums) / len(nums)
    variance = sum((x - mean) ** 2 for x in nums) / len(nums)
    std = variance ** 0.5 or 1.0
    for row, val in zip(buffered, values):
        if val is None:
            yield {**row, output_col: "false"}
        else:
            z = abs((val - mean) / std)
            yield {**row, output_col: "true" if z > threshold else "false"}


def flag_iqr(rows: Iterator[dict], column: str, multiplier: float = 1.5,
             output_col: str = "is_outlier") -> Iterator[dict]:
    """Flag rows where value is outside IQR fence."""
    buffered = list(rows)
    values = [_to_float(r.get(column, "")) for r in buffered]
    nums = sorted(v for v in values if v is not None)
    if len(nums) < 4:
        for row in buffered:
            yield {**row, output_col: "false"}
        return
    mid = len(nums) // 2
    q1 = sorted(nums[:mid])[len(nums[:mid]) // 2]
    q3 = sorted(nums[mid + len(nums) % 2:])[len(nums[mid + len(nums) % 2:]) // 2]
    iqr = q3 - q1
    lo, hi = q1 - multiplier * iqr, q3 + multiplier * iqr
    for row, val in zip(buffered, values):
        if val is None:
            yield {**row, output_col: "false"}
        else:
            yield {**row, output_col: "true" if val < lo or val > hi else "false"}


def only_outliers(rows: Iterator[dict], output_col: str = "is_outlier") -> Iterator[dict]:
    """Filter to rows already flagged as outliers."""
    for row in rows:
        if row.get(output_col) == "true":
            yield row


def remove_outliers(rows: Iterator[dict], output_col: str = "is_outlier") -> Iterator[dict]:
    """Filter out rows flagged as outliers."""
    for row in rows:
        if row.get(output_col) != "true":
            yield row
