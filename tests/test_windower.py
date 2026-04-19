import pytest
from csv_surgeon.windower import rolling_mean, rolling_sum, lag_column, lead_column, rolling_window


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "val": "10"},
        {"id": "2", "val": "20"},
        {"id": "3", "val": "30"},
        {"id": "4", "val": "40"},
        {"id": "5", "val": "50"},
    ]


def test_rolling_mean_fills_initial_rows(sample_rows):
    result = list(rolling_mean(iter(sample_rows), "val", 3))
    assert result[0]["val_rolling_mean"] == ""
    assert result[1]["val_rolling_mean"] == ""


def test_rolling_mean_correct_value(sample_rows):
    result = list(rolling_mean(iter(sample_rows), "val", 3))
    assert result[2]["val_rolling_mean"] == str(round(20.0, 6))
    assert result[3]["val_rolling_mean"] == str(round(30.0, 6))


def test_rolling_mean_custom_output_column(sample_rows):
    result = list(rolling_mean(iter(sample_rows), "val", 2, output_column="avg"))
    assert "avg" in result[1]


def test_rolling_sum_correct_value(sample_rows):
    result = list(rolling_sum(iter(sample_rows), "val", 2))
    assert result[1]["val_rolling_sum"] == "30.0"
    assert result[2]["val_rolling_sum"] == "50.0"


def test_rolling_sum_fill_value(sample_rows):
    result = list(rolling_sum(iter(sample_rows), "val", 3, fill="N/A"))
    assert result[0]["val_rolling_sum"] == "N/A"


def test_rolling_window_invalid_size(sample_rows):
    with pytest.raises(ValueError):
        list(rolling_window(iter(sample_rows), "val", 0, "out", sum))


def test_rolling_window_non_numeric_fills(sample_rows):
    rows = [{"val": "abc"}, {"val": "10"}, {"val": "20"}]
    result = list(rolling_mean(iter(rows), "val", 2))
    assert result[0]["val_rolling_mean"] == ""
    assert result[1]["val_rolling_mean"] == ""


def test_lag_column_first_row_is_fill(sample_rows):
    result = list(lag_column(iter(sample_rows), "val"))
    assert result[0]["val_lag1"] == ""


def test_lag_column_correct_values(sample_rows):
    result = list(lag_column(iter(sample_rows), "val"))
    assert result[1]["val_lag1"] == "10"
    assert result[2]["val_lag1"] == "20"


def test_lag_column_periods_two(sample_rows):
    result = list(lag_column(iter(sample_rows), "val", periods=2))
    assert result[0]["val_lag2"] == ""
    assert result[1]["val_lag2"] == ""
    assert result[2]["val_lag2"] == "10"


def test_lag_column_custom_output(sample_rows):
    result = list(lag_column(iter(sample_rows), "val", output_column="prev"))
    assert "prev" in result[0]


def test_lag_column_invalid_periods(sample_rows):
    with pytest.raises(ValueError):
        list(lag_column(iter(sample_rows), "val", periods=0))


def test_lead_column_last_row_is_fill(sample_rows):
    result = list(lead_column(iter(sample_rows), "val"))
    assert result[-1]["val_lead1"] == ""


def test_lead_column_correct_values(sample_rows):
    result = list(lead_column(iter(sample_rows), "val"))
    assert result[0]["val_lead1"] == "20"
    assert result[1]["val_lead1"] == "30"


def test_lead_column_periods_two(sample_rows):
    result = list(lead_column(iter(sample_rows), "val", periods=2))
    assert result[-1]["val_lead2"] == ""
    assert result[-2]["val_lead2"] == ""
    assert result[0]["val_lead2"] == "30"


def test_lead_column_custom_output(sample_rows):
    result = list(lead_column(iter(sample_rows), "val", output_column="next"))
    assert "next" in result[0]


def test_lead_column_invalid_periods(sample_rows):
    with pytest.raises(ValueError):
        list(lead_column(iter(sample_rows), "val", periods=0))
