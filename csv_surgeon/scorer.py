"""Row scoring: assign a numeric score to each row based on weighted column rules."""
from typing import Callable, Dict, Iterable, Iterator


def _make_scorer(rules: Dict[str, Callable[[str], float]]):
    """Return a transform that adds a '__score__' column."""
    def _transform(row: dict) -> dict:
        total = 0.0
        for col, fn in rules.items():
            val = row.get(col, "")
            try:
                total += fn(val)
            except Exception:
                pass
        out = dict(row)
        out["__score__"] = str(round(total, 6))
        return out
    return _transform


def score_rows(
    rows: Iterable[dict],
    rules: Dict[str, Callable[[str], float]],
    output_column: str = "__score__",
) -> Iterator[dict]:
    """Yield each row with a score column appended."""
    transform = _make_scorer(rules)
    for row in rows:
        scored = transform(row)
        if output_column != "__score__":
            scored[output_column] = scored.pop("__score__")
        yield scored


def threshold_filter(
    rows: Iterable[dict],
    score_column: str,
    minimum: float,
) -> Iterator[dict]:
    """Yield only rows whose score meets or exceeds *minimum*."""
    for row in rows:
        try:
            if float(row.get(score_column, 0)) >= minimum:
                yield row
        except ValueError:
            pass


def rank_rows(
    rows: Iterable[dict],
    score_column: str,
    descending: bool = True,
    rank_column: str = "__rank__",
) -> Iterator[dict]:
    """Sort rows by score and add a rank column (loads all into memory)."""
    buffered = list(rows)
    buffered.sort(
        key=lambda r: float(r.get(score_column) or 0),
        reverse=descending,
    )
    for i, row in enumerate(buffered, start=1):
        out = dict(row)
        out[rank_column] = str(i)
        yield out
