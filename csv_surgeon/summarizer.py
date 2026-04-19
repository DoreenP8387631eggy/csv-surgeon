"""Column-level summary statistics for CSV streams."""
from typing import Iterable, Iterator
import math


def _to_float(value: str):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def summarize_rows(rows: Iterable[dict], columns: list[str] | None = None) -> dict:
    """Compute summary stats for each column. Returns a dict keyed by column name."""
    stats: dict[str, dict] = {}
    count = 0

    for row in rows:
        count += 1
        cols = columns if columns else list(row.keys())
        for col in cols:
            if col not in stats:
                stats[col] = {"count": 0, "non_empty": 0, "numeric_count": 0,
                              "sum": 0.0, "min": None, "max": None, "_sq_sum": 0.0}
            s = stats[col]
            s["count"] += 1
            val = row.get(col, "")
            if val.strip():
                s["non_empty"] += 1
            n = _to_float(val)
            if n is not None:
                s["numeric_count"] += 1
                s["sum"] += n
                s["_sq_sum"] += n * n
                s["min"] = n if s["min"] is None else min(s["min"], n)
                s["max"] = n if s["max"] is None else max(s["max"], n)

    for col, s in stats.items():
        nc = s["numeric_count"]
        s["mean"] = (s["sum"] / nc) if nc else None
        if nc > 1:
            variance = (s["_sq_sum"] - (s["sum"] ** 2) / nc) / (nc - 1)
            s["stddev"] = math.sqrt(max(variance, 0.0))
        else:
            s["stddev"] = None
        s["empty"] = s["count"] - s["non_empty"]
        del s["_sq_sum"]

    return stats


def summary_to_rows(stats: dict) -> Iterator[dict]:
    """Convert summary dict to a stream of rows suitable for CSV output."""
    for col, s in stats.items():
        yield {
            "column": col,
            "count": str(s["count"]),
            "non_empty": str(s["non_empty"]),
            "empty": str(s["empty"]),
            "numeric_count": str(s["numeric_count"]),
            "sum": str(round(s["sum"], 6)) if s["numeric_count"] else "",
            "mean": str(round(s["mean"], 6)) if s["mean"] is not None else "",
            "stddev": str(round(s["stddev"], 6)) if s["stddev"] is not None else "",
            "min": str(s["min"]) if s["min"] is not None else "",
            "max": str(s["max"]) if s["max"] is not None else "",
        }
