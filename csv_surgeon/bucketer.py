"""Bucketing / binning utilities for numeric columns."""
from typing import Iterator, Dict, Any, List, Tuple, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def bucket_column(
    rows: Iterator[Dict[str, Any]],
    column: str,
    edges: List[float],
    labels: Optional[List[str]] = None,
    output_column: str = "bucket",
    default: str = "",
) -> Iterator[Dict[str, Any]]:
    """Assign each row to a bucket based on numeric bin edges (left-inclusive)."""
    if labels and len(labels) != len(edges) - 1:
        raise ValueError("len(labels) must equal len(edges) - 1")
    sorted_edges = sorted(edges)
    for row in rows:
        out = dict(row)
        val = _to_float(row.get(column, ""))
        if val is None:
            out[output_column] = default
        else:
            assigned = default
            for i in range(len(sorted_edges) - 1):
                if sorted_edges[i] <= val < sorted_edges[i + 1]:
                    assigned = labels[i] if labels else f"{sorted_edges[i]}-{sorted_edges[i+1]}"
                    break
            else:
                if val == sorted_edges[-1]:
                    idx = len(sorted_edges) - 2
                    assigned = labels[idx] if labels else f"{sorted_edges[idx]}-{sorted_edges[-1]}"
            out[output_column] = assigned
        yield out


def quantile_bucket(
    rows: List[Dict[str, Any]],
    column: str,
    n_buckets: int = 4,
    output_column: str = "quantile",
    default: str = "",
) -> Iterator[Dict[str, Any]]:
    """Assign rows to quantile buckets (requires full materialisation)."""
    values = [_to_float(r.get(column, "")) for r in rows]
    numeric = sorted(v for v in values if v is not None)
    if not numeric:
        for row in rows:
            yield {**row, output_column: default}
        return
    size = len(numeric)
    edges = [numeric[int(i * size / n_buckets)] for i in range(n_buckets)] + [numeric[-1] + 1]
    labels = [f"Q{i+1}" for i in range(n_buckets)]
    yield from bucket_column(iter(rows), column, edges, labels, output_column, default)
