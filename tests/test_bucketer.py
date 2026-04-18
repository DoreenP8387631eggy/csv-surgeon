import pytest
from csv_surgeon.bucketer import bucket_column, quantile_bucket


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "score": "15"},
        {"name": "Bob", "score": "45"},
        {"name": "Carol", "score": "75"},
        {"name": "Dave", "score": "95"},
        {"name": "Eve", "score": ""},
    ]


def apply(rows, **kwargs):
    return list(bucket_column(iter(rows), **kwargs))


def test_bucket_column_assigns_correct_bucket(sample_rows):
    result = apply(sample_rows, column="score", edges=[0, 33, 66, 100], labels=["low", "mid", "high"])
    assert result[0]["bucket"] == "low"
    assert result[1]["bucket"] == "mid"
    assert result[2]["bucket"] == "high"


def test_bucket_column_default_label_format(sample_rows):
    result = apply(sample_rows[:1], column="score", edges=[0, 50, 100])
    assert result[0]["bucket"] == "0-50"


def test_bucket_column_non_numeric_uses_default(sample_rows):
    result = apply(sample_rows, column="score", edges=[0, 50, 100], default="unknown")
    assert result[4]["bucket"] == "unknown"


def test_bucket_column_custom_output_column(sample_rows):
    result = apply(sample_rows[:1], column="score", edges=[0, 100], labels=["all"], output_column="tier")
    assert "tier" in result[0]
    assert "bucket" not in result[0]


def test_bucket_column_preserves_original_fields(sample_rows):
    result = apply(sample_rows[:1], column="score", edges=[0, 100], labels=["all"])
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == "15"


def test_bucket_column_wrong_label_count_raises():
    with pytest.raises(ValueError):
        list(bucket_column(iter([{"score": "10"}]), "score", [0, 50, 100], labels=["only_one"]))


def test_bucket_column_out_of_range_uses_default(sample_rows):
    result = apply(sample_rows[3:4], column="score", edges=[0, 50], labels=["low"], default="oor")
    assert result[0]["bucket"] == "oor"


def test_quantile_bucket_assigns_four_quantiles():
    rows = [{"v": str(i)} for i in range(1, 9)]
    result = list(quantile_bucket(rows, column="v", n_buckets=4))
    quantiles = {r["quantile"] for r in result}
    assert quantiles == {"Q1", "Q2", "Q3", "Q4"}


def test_quantile_bucket_empty_column_uses_default():
    rows = [{"v": ""}, {"v": ""}]
    result = list(quantile_bucket(rows, column="v", default="none"))
    assert all(r["quantile"] == "none" for r in result)


def test_quantile_bucket_preserves_fields():
    rows = [{"name": "x", "v": str(i)} for i in range(1, 5)]
    result = list(quantile_bucket(rows, column="v"))
    assert result[0]["name"] == "x"
