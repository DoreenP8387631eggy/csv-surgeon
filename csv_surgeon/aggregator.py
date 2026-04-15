"""Aggregation utilities for streaming CSV data."""

from typing import Iterable, Dict, Any, Optional
from collections import defaultdict


def count(rows: Iterable[Dict[str, Any]], column: Optional[str] = None) -> int:
    """Count rows, optionally only where column value is non-empty."""
    total = 0
    for row in rows:
        if column is None or row.get(column, "").strip():
            total += 1
    return total


def sum_column(rows: Iterable[Dict[str, Any]], column: str) -> float:
    """Sum numeric values in a column, skipping non-numeric entries."""
    total = 0.0
    for row in rows:
        val = row.get(column, "").strip()
        try:
            total += float(val)
        except (ValueError, TypeError):
            continue
    return total


def min_column(rows: Iterable[Dict[str, Any]], column: str) -> Optional[float]:
    """Return the minimum numeric value in a column."""
    result: Optional[float] = None
    for row in rows:
        val = row.get(column, "").strip()
        try:
            num = float(val)
            if result is None or num < result:
                result = num
        except (ValueError, TypeError):
            continue
    return result


def max_column(rows: Iterable[Dict[str, Any]], column: str) -> Optional[float]:
    """Return the maximum numeric value in a column."""
    result: Optional[float] = None
    for row in rows:
        val = row.get(column, "").strip()
        try:
            num = float(val)
            if result is None or num > result:
                result = num
        except (ValueError, TypeError):
            continue
    return result


def average_column(rows: Iterable[Dict[str, Any]], column: str) -> Optional[float]:
    """Return the average of numeric values in a column."""
    total = 0.0
    count_ = 0
    for row in rows:
        val = row.get(column, "").strip()
        try:
            total += float(val)
            count_ += 1
        except (ValueError, TypeError):
            continue
    return total / count_ if count_ > 0 else None


def value_counts(rows: Iterable[Dict[str, Any]], column: str) -> Dict[str, int]:
    """Return a dict mapping each unique value in column to its frequency."""
    counts: Dict[str, int] = defaultdict(int)
    for row in rows:
        val = row.get(column, "")
        counts[val] += 1
    return dict(counts)
