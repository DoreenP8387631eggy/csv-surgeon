import pytest
from csv_surgeon.scaler import minmax_scale, zscore_scale, robust_scale


@pytest.fixture
def sample_rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "20"},
        {"name": "c", "score": "30"},
        {"name": "d", "score": "40"},
        {"name": "e", "score": "50"},
    ]


def apply(fn, rows, **kwargs):
    return list(fn(iter(rows), **kwargs))


def test_minmax_scale_range(sample_rows):
    result = apply(minmax_scale, sample_rows, column="score")
    vals = [float(r["score"]) for r in result]
    assert min(vals) == pytest.approx(0.0)
    assert max(vals) == pytest.approx(1.0)


def test_minmax_scale_custom_range(sample_rows):
    result = apply(minmax_scale, sample_rows, column="score", feature_range=(-1.0, 1.0))
    vals = [float(r["score"]) for r in result]
    assert min(vals) == pytest.approx(-1.0)
    assert max(vals) == pytest.approx(1.0)


def test_minmax_scale_out_col(sample_rows):
    result = apply(minmax_scale, sample_rows, column="score", out_col="score_scaled")
    assert "score_scaled" in result[0]
    assert result[0]["score"] == "10"  # original preserved


def test_minmax_scale_non_numeric_becomes_empty():
    rows = [{"val": "abc"}, {"val": "10"}, {"val": "20"}]
    result = apply(minmax_scale, rows, column="val")
    assert result[0]["val"] == ""


def test_minmax_scale_all_non_numeric_passthrough():
    rows = [{"val": "x"}, {"val": "y"}]
    result = apply(minmax_scale, rows, column="val")
    assert result == rows


def test_zscore_scale_mean_near_zero(sample_rows):
    result = apply(zscore_scale, sample_rows, column="score")
    vals = [float(r["score"]) for r in result]
    assert sum(vals) == pytest.approx(0.0, abs=1e-9)


def test_zscore_scale_out_col(sample_rows):
    result = apply(zscore_scale, sample_rows, column="score", out_col="z")
    assert "z" in result[0]
    assert result[0]["score"] == "10"


def test_zscore_scale_non_numeric_becomes_empty():
    rows = [{"v": "bad"}, {"v": "10"}, {"v": "20"}]
    result = apply(zscore_scale, rows, column="v")
    assert result[0]["v"] == ""


def test_robust_scale_preserves_row_count(sample_rows):
    result = apply(robust_scale, sample_rows, column="score")
    assert len(result) == 5


def test_robust_scale_out_col(sample_rows):
    result = apply(robust_scale, sample_rows, column="score", out_col="robust")
    assert "robust" in result[0]
    assert result[0]["score"] == "10"


def test_robust_scale_all_non_numeric_passthrough():
    rows = [{"v": "a"}, {"v": "b"}]
    result = apply(robust_scale, rows, column="v")
    assert result == rows


def test_minmax_scale_preserves_other_columns(sample_rows):
    result = apply(minmax_scale, sample_rows, column="score")
    assert result[0]["name"] == "a"
