import pytest
from csv_surgeon.profiler import profile_rows, profile_to_rows


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "age": "30", "score": "95.5"},
        {"name": "Bob",   "age": "25", "score": ""},
        {"name": "Carol", "age": "30", "score": "88.0"},
        {"name": "",      "age": "40", "score": "72.0"},
    ]


def test_profile_count(sample_rows):
    p = profile_rows(sample_rows)
    assert p["name"]["count"] == 4
    assert p["age"]["count"] == 4


def test_profile_non_empty(sample_rows):
    p = profile_rows(sample_rows)
    assert p["name"]["non_empty"] == 3
    assert p["score"]["non_empty"] == 3


def test_profile_empty(sample_rows):
    p = profile_rows(sample_rows)
    assert p["name"]["empty"] == 1
    assert p["score"]["empty"] == 1


def test_profile_unique(sample_rows):
    p = profile_rows(sample_rows)
    assert p["age"]["unique"] == 3  # 25, 30, 40
    assert p["name"]["unique"] == 4  # Alice, Bob, Carol, ""


def test_profile_numeric_count(sample_rows):
    p = profile_rows(sample_rows)
    assert p["age"]["numeric_count"] == 4
    assert p["score"]["numeric_count"] == 3
    assert p["name"]["numeric_count"] == 0


def test_profile_mean(sample_rows):
    p = profile_rows(sample_rows)
    assert p["age"]["mean"] == pytest.approx((30 + 25 + 30 + 40) / 4)


def test_profile_min_max(sample_rows):
    p = profile_rows(sample_rows)
    assert p["age"]["min"] == 25.0
    assert p["age"]["max"] == 40.0


def test_profile_non_numeric_has_none_stats(sample_rows):
    p = profile_rows(sample_rows)
    assert p["name"]["sum"] is None
    assert p["name"]["mean"] is None
    assert p["name"]["min"] is None


def test_profile_to_rows_yields_one_row_per_column(sample_rows):
    p = profile_rows(sample_rows)
    rows = list(profile_to_rows(p))
    assert len(rows) == 3
    cols = {r["column"] for r in rows}
    assert cols == {"name", "age", "score"}


def test_profile_to_rows_contains_expected_keys(sample_rows):
    p = profile_rows(sample_rows)
    rows = list(profile_to_rows(p))
    for row in rows:
        assert "count" in row
        assert "mean" in row
        assert "min" in row
        assert "max" in row


def test_profile_empty_stream():
    p = profile_rows([])
    assert p == {}
