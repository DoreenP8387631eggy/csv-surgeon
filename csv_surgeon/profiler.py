"""Column profiling: compute basic stats for each column in a stream."""
from collections import defaultdict
from typing import Iterable, Iterator


def profile_rows(
    rows: Iterable[dict],
) -> dict:
    """Consume all rows and return a profile dict keyed by column name."""
    counts: dict = defaultdict(int)
    non_empty: dict = defaultdict(int)
    numeric_sum: dict = defaultdict(float)
    numeric_count: dict = defaultdict(int)
    min_val: dict = {}
    max_val: dict = {}
    unique: dict = defaultdict(set)
    total = 0

    for row in rows:
        total += 1
        for col, val in row.items():
            counts[col] += 1
            if val and val.strip():
                non_empty[col] += 1
            try:
                num = float(val)
                numeric_sum[col] += num
                numeric_count[col] += 1
                if col not in min_val or num < min_val[col]:
                    min_val[col] = num
                if col not in max_val or num > max_val[col]:
                    max_val[col] = num
            except (ValueError, TypeError):
                pass
            unique[col].add(val)

    profile = {}
    for col in counts:
        n = counts[col]
        nc = numeric_count.get(col, 0)
        profile[col] = {
            "count": n,
            "non_empty": non_empty[col],
            "empty": n - non_empty[col],
            "unique": len(unique[col]),
            "numeric_count": nc,
            "sum": numeric_sum[col] if nc else None,
            "mean": numeric_sum[col] / nc if nc else None,
            "min": min_val.get(col),
            "max": max_val.get(col),
        }
    return profile


def profile_to_rows(profile: dict) -> Iterator[dict]:
    """Convert a profile dict into an iterable of flat dicts (for CSV output)."""
    for col, stats in profile.items():
        row = {"column": col}
        row.update({k: ("" if v is None else str(v)) for k, v in stats.items()})
        yield row
