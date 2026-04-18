import pytest
from csv_surgeon.interpolator import interpolate_column, ffill_column, bfill_column


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "value": "10"},
        {"id": "2", "value": ""},
        {"id": "3", "value": ""},
        {"id": "4", "value": "40"},
        {"id": "5", "value": ""},
    ]


def apply(fn, rows):
    return list(fn(iter(rows)))


# --- linear interpolation ---

def test_linear_fills_middle_gaps(sample_rows):
    result = apply(interpolate_column("value"), sample_rows)
    assert result[1]["value"] == str(round(10 + (1/3) * 30, 10))
    assert result[2]["value"] == str(round(10 + (2/3) * 30, 10))


def test_linear_preserves_known_values(sample_rows):
    result = apply(interpolate_column("value"), sample_rows)
    assert result[0]["value"] == "10"
    assert result[3]["value"] == "40"


def test_linear_trailing_gap_uses_last_known(sample_rows):
    result = apply(interpolate_column("value"), sample_rows)
    assert result[4]["value"] == "40"


def test_linear_all_empty_uses_fill_value():
    rows = [{"v": ""}, {"v": ""}, {"v": ""}]
    result = apply(interpolate_column("v", fill_value="0"), rows)
    assert all(r["v"] == "0" for r in result)


def test_linear_no_gaps_unchanged():
    rows = [{"v": "1"}, {"v": "2"}, {"v": "3"}]
    result = apply(interpolate_column("v"), rows)
    assert [r["v"] for r in result] == ["1", "2", "3"]


def test_linear_empty_stream():
    assert apply(interpolate_column("v"), []) == []


def test_linear_missing_column_uses_fill_value():
    rows = [{"other": "x"}, {"other": "y"}]
    result = apply(interpolate_column("v", fill_value="N/A"), rows)
    assert all(r["v"] == "N/A" for r in result)


# --- ffill ---

def test_ffill_propagates_value_forward(sample_rows):
    result = apply(ffill_column("value"), sample_rows)
    assert result[1]["value"] == "10"
    assert result[2]["value"] == "10"


def test_ffill_no_prior_value_uses_fill():
    rows = [{"v": ""}, {"v": "5"}, {"v": ""}]
    result = apply(ffill_column("v", fill_value="0"), rows)
    assert result[0]["v"] == "0"
    assert result[1]["v"] == "5"
    assert result[2]["v"] == "5"


def test_ffill_does_not_mutate_input(sample_rows):
    original = [dict(r) for r in sample_rows]
    apply(ffill_column("value"), sample_rows)
    assert sample_rows == original


# --- bfill ---

def test_bfill_propagates_value_backward():
    rows = [{"v": ""}, {"v": ""}, {"v": "30"}]
    result = apply(bfill_column("v"), rows)
    assert result[0]["v"] == "30"
    assert result[1]["v"] == "30"
    assert result[2]["v"] == "30"


def test_bfill_no_next_value_uses_fill():
    rows = [{"v": "10"}, {"v": ""}, {"v": ""}]
    result = apply(bfill_column("v", fill_value="N/A"), rows)
    assert result[1]["v"] == "N/A"
    assert result[2]["v"] == "N/A"


def test_bfill_empty_stream():
    assert apply(bfill_column("v"), []) == []
