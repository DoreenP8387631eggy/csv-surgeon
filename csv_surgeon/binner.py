"""Fixed-width and custom-label binning for numeric columns."""
from typing import Iterable, Iterator, List, Optional, Tuple


def _to_float(val: str) -> Optional[float]:
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def bin_equal_width(
    rows: Iterable[dict],
    column: str,
    n_bins: int,
    min_val: float,
    max_val: float,
    out_col: str = "bin",
    default: str = "",
) -> Iterator[dict]:
    """Assign each row to one of n equal-width bins between min_val and max_val."""
    width = (max_val - min_val) / n_bins if n_bins > 0 else 1
    for row in rows:
        v = _to_float(row.get(column, ""))
        out = default
        if v is not None:
            idx = int((v - min_val) / width)
            idx = max(0, min(idx, n_bins - 1))
            lo = min_val + idx * width
            hi = lo + width
            out = f"[{lo:.4g}, {hi:.4g})"
        yield {**row, out_col: out}


def bin_custom(
    rows: Iterable[dict],
    column: str,
    edges: List[float],
    labels: Optional[List[str]] = None,
    out_col: str = "bin",
    default: str = "",
) -> Iterator[dict]:
    """Bin values into custom intervals defined by edges (sorted ascending).
    len(labels) must equal len(edges) - 1 if provided.
    """
    edges = sorted(edges)
    n = len(edges) - 1
    if labels is None:
        labels = [f"[{edges[i]:.4g}, {edges[i+1]:.4g})" for i in range(n)]
    for row in rows:
        v = _to_float(row.get(column, ""))
        out = default
        if v is not None:
            for i in range(n):
                lo, hi = edges[i], edges[i + 1]
                if lo <= v < hi or (i == n - 1 and v == hi):
                    out = labels[i]
                    break
        yield {**row, out_col: out}


def bin_labels(
    rows: Iterable[dict],
    column: str,
    thresholds: List[Tuple[float, str]],
    out_col: str = "bin",
    default: str = "other",
) -> Iterator[dict]:
    """Assign label for the first threshold where value <= threshold."""
    thresholds = sorted(thresholds, key=lambda t: t[0])
    for row in rows:
        v = _to_float(row.get(column, ""))
        out = default
        if v is not None:
            for limit, label in thresholds:
                if v <= limit:
                    out = label
                    break
        yield {**row, out_col: out}
