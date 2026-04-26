"""Fuzzy join utilities for csv-surgeon.

Provides join operations that match rows based on approximate string
similarity rather than exact key equality.  Useful when joining datasets
that contain slightly different spellings, abbreviations, or casing.
"""

from __future__ import annotations

from typing import Dict, Generator, Iterable, List, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _similarity(a: str, b: str) -> float:
    """Return a simple character-overlap similarity score in [0.0, 1.0].

    Uses a bigram-based Dice coefficient so that short strings are not
    unfairly penalised and the metric is symmetric.
    """
    a, b = a.lower().strip(), b.lower().strip()
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0

    def bigrams(s: str) -> List[str]:
        return [s[i:i + 2] for i in range(len(s) - 1)]

    bg_a = bigrams(a)
    bg_b = bigrams(b)
    if not bg_a or not bg_b:
        # Fall back to character overlap for single-char strings
        return 1.0 if a == b else 0.0

    set_a = {}
    for g in bg_a:
        set_a[g] = set_a.get(g, 0) + 1

    intersection = 0
    for g in bg_b:
        if set_a.get(g, 0) > 0:
            intersection += 1
            set_a[g] -= 1

    return (2 * intersection) / (len(bg_a) + len(bg_b))


def _index_rows(rows: Iterable[Dict[str, str]], key: str) -> Dict[str, List[Dict[str, str]]]:
    """Group *rows* by the value of *key*, returning a mapping."""
    index: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        val = row.get(key, "")
        index.setdefault(val, []).append(row)
    return index


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def fuzzy_inner_join(
    left_rows: Iterable[Dict[str, str]],
    right_rows: Iterable[Dict[str, str]],
    left_key: str,
    right_key: str,
    threshold: float = 0.75,
    score_col: Optional[str] = None,
) -> Generator[Dict[str, str], None, None]:
    """Yield merged rows where left and right keys are *similar enough*.

    Only rows whose similarity score meets *threshold* are emitted
    (inner-join semantics).  When multiple right rows match, the one with
    the highest similarity score is used.

    Parameters
    ----------
    left_rows:
        Iterable of left-hand dicts.
    right_rows:
        Iterable of right-hand dicts (consumed into memory for indexing).
    left_key:
        Column name in the left stream used for matching.
    right_key:
        Column name in the right stream used for matching.  This column is
        dropped from the output to avoid duplication.
    threshold:
        Minimum similarity score (0.0–1.0) required for a match.
    score_col:
        If provided, the similarity score is written into this output column.
    """
    index = _index_rows(right_rows, right_key)
    right_keys = list(index.keys())

    for left_row in left_rows:
        lval = left_row.get(left_key, "")
        best_score = -1.0
        best_candidates: List[Dict[str, str]] = []

        for rkey in right_keys:
            score = _similarity(lval, rkey)
            if score >= threshold and score > best_score:
                best_score = score
                best_candidates = index[rkey]

        for right_row in best_candidates:
            merged = {**left_row}
            for k, v in right_row.items():
                if k != right_key:
                    merged[k] = v
            if score_col:
                merged[score_col] = f"{best_score:.4f}"
            yield merged


def fuzzy_left_join(
    left_rows: Iterable[Dict[str, str]],
    right_rows: Iterable[Dict[str, str]],
    left_key: str,
    right_key: str,
    threshold: float = 0.75,
    score_col: Optional[str] = None,
) -> Generator[Dict[str, str], None, None]:
    """Yield all left rows, enriched with the best fuzzy match from right.

    Rows with no match above *threshold* are still emitted; right-side
    columns will be empty strings for those rows.

    Parameters mirror :func:`fuzzy_inner_join`.
    """
    index = _index_rows(right_rows, right_key)
    right_keys = list(index.keys())

    # Determine right-side column names (excluding the join key)
    right_cols: List[str] = []
    for candidates in index.values():
        if candidates:
            right_cols = [k for k in candidates[0] if k != right_key]
            break

    for left_row in left_rows:
        lval = left_row.get(left_key, "")
        best_score = -1.0
        best_candidates: List[Dict[str, str]] = []

        for rkey in right_keys:
            score = _similarity(lval, rkey)
            if score >= threshold and score > best_score:
                best_score = score
                best_candidates = index[rkey]

        if best_candidates:
            for right_row in best_candidates:
                merged = {**left_row}
                for k, v in right_row.items():
                    if k != right_key:
                        merged[k] = v
                if score_col:
                    merged[score_col] = f"{best_score:.4f}"
                yield merged
        else:
            merged = {**left_row}
            for col in right_cols:
                merged.setdefault(col, "")
            if score_col:
                merged[score_col] = ""
            yield merged
