"""Column value frequency counter for CSV streams."""
from collections import Counter
from typing import Iterable, Iterator


def count_values(rows: Iterable[dict], column: str) -> dict:
    """Count occurrences of each unique value in a column.

    Returns a dict mapping value -> count, sorted by count descending.
    """
    counter: Counter = Counter()
    for row in rows:
        value = row.get(column, "")
        counter[value] += 1
    return dict(counter.most_common())


def count_values_multi(rows: Iterable[dict], columns: list[str]) -> dict:
    """Count occurrences of unique value combinations across multiple columns.

    Returns a dict mapping tuple-of-values -> count, sorted by count descending.
    """
    counter: Counter = Counter()
    for row in rows:
        key = tuple(row.get(col, "") for col in columns)
        counter[key] += 1
    return dict(counter.most_common())


def frequency_rows(rows: Iterable[dict], column: str) -> Iterator[dict]:
    """Yield rows representing value frequencies for a column.

    Each output row has 'value', 'count', and 'percent' fields.
    """
    counts = count_values(rows, column)
    total = sum(counts.values())
    for value, cnt in counts.items():
        yield {
            "value": value,
            "count": str(cnt),
            "percent": f"{100 * cnt / total:.2f}" if total else "0.00",
        }
