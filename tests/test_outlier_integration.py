"""Integration tests combining outlier detection with other pipeline steps."""
from csv_surgeon.outlier import flag_zscore, flag_iqr, only_outliers, remove_outliers
from csv_surgeon.normalizer import to_lowercase


def _make_rows(values):
    return [{"id": str(i), "score": str(v), "label": "Item"} for i, v in enumerate(values)]


def test_flag_then_filter_outliers():
    rows = _make_rows([5, 6, 5, 7, 6, 5, 200])
    flagged = list(flag_zscore(iter(rows), "score", threshold=2.0))
    outliers = list(only_outliers(iter(flagged)))
    assert len(outliers) == 1
    assert outliers[0]["score"] == "200"


def test_flag_then_remove_outliers_count():
    rows = _make_rows([5, 6, 5, 7, 6, 5, 200])
    flagged = list(flag_zscore(iter(rows), "score", threshold=2.0))
    clean = list(remove_outliers(iter(flagged)))
    assert len(clean) == len(rows) - 1


def test_iqr_then_remove_preserves_normal_values():
    rows = _make_rows([10, 11, 10, 12, 11, 10, 500])
    flagged = list(flag_iqr(iter(rows), "score"))
    clean = list(remove_outliers(iter(flagged)))
    assert all(r["score"] != "500" for r in clean)


def test_pipeline_preserves_all_columns():
    rows = _make_rows([1, 2, 3, 4, 50])
    flagged = list(flag_zscore(iter(rows), "score", threshold=1.5))
    for row in flagged:
        assert "id" in row
        assert "label" in row
        assert "is_outlier" in row


def test_empty_stream_produces_no_output():
    result = list(flag_zscore(iter([]), "score"))
    assert result == []
