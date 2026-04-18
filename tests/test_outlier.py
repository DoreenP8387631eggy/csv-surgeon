import pytest
from csv_surgeon.outlier import flag_zscore, flag_iqr, only_outliers, remove_outliers


@pytest.fixture
def numeric_rows():
    values = [10, 12, 11, 13, 10, 12, 11, 100]  # 100 is outlier
    return [{"id": str(i), "val": str(v)} for i, v in enumerate(values)]


def test_zscore_flags_outlier(numeric_rows):
    result = list(flag_zscore(iter(numeric_rows), "val", threshold=2.0))
    assert result[-1]["is_outlier"] == "true"


def test_zscore_non_outliers_flagged_false(numeric_rows):
    result = list(flag_zscore(iter(numeric_rows), "val", threshold=2.0))
    for row in result[:-1]:
        assert row["is_outlier"] == "false"


def test_zscore_preserves_original_fields(numeric_rows):
    result = list(flag_zscore(iter(numeric_rows), "val"))
    assert all("id" in r and "val" in r for r in result)


def test_zscore_custom_output_col(numeric_rows):
    result = list(flag_zscore(iter(numeric_rows), "val", output_col="outlier_flag"))
    assert "outlier_flag" in result[0]


def test_zscore_missing_column_flags_false():
    rows = [{"x": "1"}, {"x": "2"}]
    result = list(flag_zscore(iter(rows), "missing"))
    assert all(r["is_outlier"] == "false" for r in result)


def test_zscore_too_few_rows():
    rows = [{"val": "5"}]
    result = list(flag_zscore(iter(rows), "val"))
    assert result[0]["is_outlier"] == "false"


def test_iqr_flags_outlier(numeric_rows):
    result = list(flag_iqr(iter(numeric_rows), "val"))
    assert result[-1]["is_outlier"] == "true"


def test_iqr_non_outliers_false(numeric_rows):
    result = list(flag_iqr(iter(numeric_rows), "val"))
    for row in result[:-1]:
        assert row["is_outlier"] == "false"


def test_iqr_custom_multiplier(numeric_rows):
    result_strict = list(flag_iqr(iter(numeric_rows), "val", multiplier=0.1))
    flagged = [r for r in result_strict if r["is_outlier"] == "true"]
    assert len(flagged) >= 1


def test_only_outliers_filters_correctly(numeric_rows):
    flagged = list(flag_zscore(iter(numeric_rows), "val", threshold=2.0))
    result = list(only_outliers(iter(flagged)))
    assert len(result) == 1
    assert result[0]["val"] == "100"


def test_remove_outliers_excludes_flagged(numeric_rows):
    flagged = list(flag_zscore(iter(numeric_rows), "val", threshold=2.0))
    result = list(remove_outliers(iter(flagged)))
    assert all(r["val"] != "100" for r in result)
    assert len(result) == len(numeric_rows) - 1
