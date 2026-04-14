"""Row filtering utilities for csv-surgeon."""

from typing import Callable, Dict, Any, List, Optional
import re


RowFilter = Callable[[Dict[str, Any]], bool]


def equals(column: str, value: str) -> RowFilter:
    """Return a filter that matches rows where column equals value."""
    def _filter(row: Dict[str, Any]) -> bool:
        return row.get(column) == value
    return _filter


def not_equals(column: str, value: str) -> RowFilter:
    """Return a filter that matches rows where column does not equal value."""
    def _filter(row: Dict[str, Any]) -> bool:
        return row.get(column) != value
    return _filter


def contains(column: str, substring: str) -> RowFilter:
    """Return a filter that matches rows where column contains substring."""
    def _filter(row: Dict[str, Any]) -> bool:
        val = row.get(column, "")
        return substring in (val or "")
    return _filter


def matches_regex(column: str, pattern: str) -> RowFilter:
    """Return a filter that matches rows where column matches a regex pattern."""
    compiled = re.compile(pattern)

    def _filter(row: Dict[str, Any]) -> bool:
        val = row.get(column, "")
        return bool(compiled.search(val or ""))
    return _filter


def greater_than(column: str, value: float) -> RowFilter:
    """Return a filter that matches rows where column (numeric) > value."""
    def _filter(row: Dict[str, Any]) -> bool:
        try:
            return float(row.get(column, "")) > value
        except (ValueError, TypeError):
            return False
    return _filter


def less_than(column: str, value: float) -> RowFilter:
    """Return a filter that matches rows where column (numeric) < value."""
    def _filter(row: Dict[str, Any]) -> bool:
        try:
            return float(row.get(column, "")) < value
        except (ValueError, TypeError):
            return False
    return _filter


def all_of(filters: List[RowFilter]) -> RowFilter:
    """Combine multiple filters with AND logic."""
    def _filter(row: Dict[str, Any]) -> bool:
        return all(f(row) for f in filters)
    return _filter


def any_of(filters: List[RowFilter]) -> RowFilter:
    """Combine multiple filters with OR logic."""
    def _filter(row: Dict[str, Any]) -> bool:
        return any(f(row) for f in filters)
    return _filter


def negate(f: RowFilter) -> RowFilter:
    """Negate a filter."""
    def _filter(row: Dict[str, Any]) -> bool:
        return not f(row)
    return _filter
