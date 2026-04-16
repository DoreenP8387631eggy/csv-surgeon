import pytest
from csv_surgeon.formatter import format_column, zero_pad, number_format, date_reformat


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "price": "9.5", "date": "2024-01-15", "code": "42"},
        {"id": "2", "price": "100", "date": "2024-12-03", "code": "7"},
        {"id": "3", "price": "abc", "date": "bad-date", "code": "999"},
    ]


def apply(transform, rows):
    return list(transform(iter(rows)))


def test_format_column_wraps_value(sample_rows):
    result = apply(format_column("id", "ID-{value}"), sample_rows)
    assert result[0]["id"] == "ID-1"
    assert result[1]["id"] == "ID-2"


def test_format_column_missing_column_is_noop(sample_rows):
    result = apply(format_column("missing", "X-{value}"), sample_rows)
    assert "missing" not in result[0]


def test_format_column_does_not_mutate_original(sample_rows):
    original = dict(sample_rows[0])
    apply(format_column("id", "X-{value}"), sample_rows)
    assert sample_rows[0] == original


def test_zero_pad_pads_short_numbers(sample_rows):
    result = apply(zero_pad("code", 5), sample_rows)
    assert result[0]["code"] == "00042"
    assert result[1]["code"] == "00007"


def test_zero_pad_does_not_shorten(sample_rows):
    result = apply(zero_pad("code", 2), sample_rows)
    assert result[2]["code"] == "999"


def test_zero_pad_skips_non_numeric(sample_rows):
    rows = [{"code": "abc"}]
    result = apply(zero_pad("code", 5), rows)
    assert result[0]["code"] == "abc"


def test_number_format_two_decimals(sample_rows):
    result = apply(number_format("price", decimals=2), sample_rows)
    assert result[0]["price"] == "9.50"
    assert result[1]["price"] == "100.00"


def test_number_format_non_numeric_unchanged(sample_rows):
    result = apply(number_format("price", decimals=2), sample_rows)
    assert result[2]["price"] == "abc"


def test_number_format_thousands_separator():
    rows = [{"val": "1234567.8"}]
    result = apply(number_format("val", decimals=2, thousands_sep=True), rows)
    assert result[0]["val"] == "1,234,567.80"


def test_date_reformat_converts_format(sample_rows):
    result = apply(date_reformat("date", "%Y-%m-%d", "%d/%m/%Y"), sample_rows)
    assert result[0]["date"] == "15/01/2024"
    assert result[1]["date"] == "03/12/2024"


def test_date_reformat_bad_date_unchanged(sample_rows):
    result = apply(date_reformat("date", "%Y-%m-%d", "%d/%m/%Y"), sample_rows)
    assert result[2]["date"] == "bad-date"


def test_date_reformat_missing_column_is_noop():
    rows = [{"other": "val"}]
    result = apply(date_reformat("date", "%Y-%m-%d", "%d/%m/%Y"), rows)
    assert "date" not in result[0]
