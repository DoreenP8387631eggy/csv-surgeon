import pytest
from csv_surgeon.scorer import score_rows, threshold_filter, rank_rows


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "age": "30", "salary": "90000"},
        {"name": "Bob",   "age": "25", "salary": "50000"},
        {"name": "Carol", "age": "40", "salary": "120000"},
    ]


def _age_score(val):
    return float(val) / 10


def _salary_score(val):
    return float(val) / 100000


def test_score_rows_adds_score_column(sample_rows):
    result = list(score_rows(sample_rows, {"age": _age_score}))
    assert all("__score__" in r for r in result)


def test_score_rows_correct_value(sample_rows):
    result = list(score_rows(sample_rows, {"age": _age_score}))
    assert float(result[0]["__score__"]) == pytest.approx(3.0)
    assert float(result[1]["__score__"]) == pytest.approx(2.5)


def test_score_rows_multi_rule(sample_rows):
    rules = {"age": _age_score, "salary": _salary_score}
    result = list(score_rows(sample_rows, rules))
    expected = 30 / 10 + 90000 / 100000
    assert float(result[0]["__score__"]) == pytest.approx(expected)


def test_score_rows_custom_output_column(sample_rows):
    result = list(score_rows(sample_rows, {"age": _age_score}, output_column="score"))
    assert "score" in result[0]
    assert "__score__" not in result[0]


def test_score_rows_missing_column_skips(sample_rows):
    result = list(score_rows(sample_rows, {"nonexistent": float}))
    assert all(float(r["__score__"]) == 0.0 for r in result)


def test_score_rows_does_not_mutate_original(sample_rows):
    original = [dict(r) for r in sample_rows]
    list(score_rows(sample_rows, {"age": _age_score}))
    assert sample_rows == original


def test_threshold_filter_keeps_high_scores():
    rows = [
        {"x": "a", "score": "5.0"},
        {"x": "b", "score": "2.0"},
        {"x": "c", "score": "3.5"},
    ]
    result = list(threshold_filter(rows, "score", minimum=3.5))
    assert len(result) == 2
    assert result[0]["x"] == "a"
    assert result[1]["x"] == "c"


def test_threshold_filter_excludes_all_below():
    rows = [{"score": "1.0"}, {"score": "0.5"}]
    result = list(threshold_filter(rows, "score", minimum=2.0))
    assert result == []


def test_rank_rows_assigns_rank(sample_rows):
    scored = list(score_rows(sample_rows, {"salary": _salary_score}))
    ranked = list(rank_rows(scored, "__score__"))
    assert all("__rank__" in r for r in ranked)


def test_rank_rows_descending_order(sample_rows):
    scored = list(score_rows(sample_rows, {"salary": _salary_score}))
    ranked = list(rank_rows(scored, "__score__", descending=True))
    assert ranked[0]["name"] == "Carol"
    assert ranked[-1]["name"] == "Bob"


def test_rank_rows_ascending_order(sample_rows):
    scored = list(score_rows(sample_rows, {"salary": _salary_score}))
    ranked = list(rank_rows(scored, "__score__", descending=False))
    assert ranked[0]["name"] == "Bob"


def test_rank_rows_custom_rank_column(sample_rows):
    scored = list(score_rows(sample_rows, {"age": _age_score}))
    ranked = list(rank_rows(scored, "__score__", rank_column="position"))
    assert "position" in ranked[0]
