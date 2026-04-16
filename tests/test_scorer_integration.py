"""Integration: score → filter → rank pipeline."""
from csv_surgeon.scorer import score_rows, threshold_filter, rank_rows


ROWS = [
    {"product": "A", "price": "10", "quantity": "5"},
    {"product": "B", "price": "20", "quantity": "2"},
    {"product": "C", "price": "15", "quantity": "8"},
    {"product": "D", "price": "5",  "quantity": "1"},
]


def _revenue(val):
    return float(val)


def test_full_pipeline_produces_ranked_results():
    rules = {"price": _revenue, "quantity": _revenue}
    scored = score_rows(ROWS, rules, output_column="score")
    filtered = threshold_filter(scored, "score", minimum=20.0)
    ranked = list(rank_rows(filtered, "score", rank_column="rank"))
    assert len(ranked) >= 1
    assert all("rank" in r for r in ranked)
    assert int(ranked[0]["rank"]) == 1


def test_full_pipeline_rank_order_is_descending():
    rules = {"price": _revenue}
    scored = score_rows(ROWS, rules, output_column="score")
    ranked = list(rank_rows(scored, "score", descending=True))
    scores = [float(r["score"]) for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_pipeline_preserves_original_columns():
    rules = {"price": _revenue}
    scored = list(score_rows(ROWS, rules, output_column="score"))
    assert all("product" in r and "price" in r and "quantity" in r for r in scored)


def test_threshold_removes_low_scorers():
    rules = {"price": _revenue}
    scored = score_rows(ROWS, rules, output_column="score")
    filtered = list(threshold_filter(scored, "score", minimum=15.0))
    products = {r["product"] for r in filtered}
    assert "D" not in products
    assert "A" not in products
