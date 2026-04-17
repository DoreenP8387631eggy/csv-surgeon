"""Row classification: assign a category label based on rule priority."""
from typing import Callable, Iterable, Iterator


def _make_predicate(column: str, operator: str, value: str) -> Callable[[dict], bool]:
    if operator == "eq":
        return lambda row: row.get(column, "") == value
    if operator == "neq":
        return lambda row: row.get(column, "") != value
    if operator == "contains":
        return lambda row: value in row.get(column, "")
    if operator == "gt":
        return lambda row: _safe_float(row.get(column, "")) > _safe_float(value)
    if operator == "lt":
        return lambda row: _safe_float(row.get(column, "")) < _safe_float(value)
    if operator == "gte":
        return lambda row: _safe_float(row.get(column, "")) >= _safe_float(value)
    if operator == "lte":
        return lambda row: _safe_float(row.get(column, "")) <= _safe_float(value)
    raise ValueError(f"Unknown operator: {operator}")


def _safe_float(v: str) -> float:
    try:
        return float(v)
    except (ValueError, TypeError):
        return float("nan")


def classify_rows(
    rows: Iterable[dict],
    rules: list[tuple[str, Callable[[dict], bool]]],
    output_column: str = "class",
    default: str = "",
) -> Iterator[dict]:
    """Assign the first matching class label to each row."""
    for row in rows:
        label = default
        for class_label, predicate in rules:
            if predicate(row):
                label = class_label
                break
        yield {**row, output_column: label}


def build_rule(
    class_label: str, column: str, operator: str, value: str
) -> tuple[str, Callable[[dict], bool]]:
    """Helper to build a (label, predicate) rule tuple."""
    return class_label, _make_predicate(column, operator, value)
