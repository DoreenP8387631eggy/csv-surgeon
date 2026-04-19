import pytest
from csv_surgeon.dateparser import parse_date_column, format_date_column, extract_date_part


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "date": "2023-06-15"},
        {"id": "2", "date": "25/12/2022"},
        {"id": "3", "date": "01/07/2021"},
        {"id": "4", "date": "bad-date"},
        {"id": "5", "date": ""},
    ]


def apply(fn, rows):
    return list(fn(rows))


def test_parse_date_iso_input(sample_rows):
    result = apply(lambda r: parse_date_column(r, "date"), sample_rows)
    assert result[0]["date"] == "2023-06-15"


def test_parse_date_dmy_slash(sample_rows):
    result = apply(lambda r: parse_date_column(r, "date"), sample_rows)
    assert result[1]["date"] == "2022-12-25"


def test_parse_date_bad_value_uses_default(sample_rows):
    result = apply(lambda r: parse_date_column(r, "date", default="N/A"), sample_rows)
    assert result[3]["date"] == "N/A"


def test_parse_date_empty_uses_default(sample_rows):
    result = apply(lambda r: parse_date_column(r, "date", default="unknown"), sample_rows)
    assert result[4]["date"] == "unknown"


def test_parse_date_output_column(sample_rows):
    result = apply(lambda r: parse_date_column(r, "date", output_column="parsed"), sample_rows)
    assert "parsed" in result[0]
    assert result[0]["date"] == "2023-06-15"  # original preserved


def test_parse_date_preserves_other_fields(sample_rows):
    result = apply(lambda r: parse_date_column(r, "date"), sample_rows)
    assert result[0]["id"] == "1"


def test_format_date_to_custom_format(sample_rows):
    result = apply(lambda r: format_date_column(r, "date", output_format="%d %b %Y"), sample_rows)
    assert result[0]["date"] == "15 Jun 2023"


def test_format_date_bad_value_uses_default(sample_rows):
    result = apply(
        lambda r: format_date_column(r, "date", output_format="%d/%m/%Y", default="-"),
        sample_rows,
    )
    assert result[3]["date"] == "-"


def test_format_date_output_column(sample_rows):
    result = apply(
        lambda r: format_date_column(r, "date", output_format="%Y", output_column="year_str"),
        sample_rows,
    )
    assert result[0]["year_str"] == "2023"


def test_extract_year(sample_rows):
    result = apply(lambda r: extract_date_part(r, "date", part="year"), sample_rows)
    assert result[0]["date_year"] == "2023"


def test_extract_month(sample_rows):
    result = apply(lambda r: extract_date_part(r, "date", part="month"), sample_rows)
    assert result[1]["date_month"] == "12"


def test_extract_weekday(sample_rows):
    result = apply(lambda r: extract_date_part(r, "date", part="weekday"), sample_rows)
    assert result[0]["date_weekday"] == "Thursday"


def test_extract_quarter(sample_rows):
    result = apply(lambda r: extract_date_part(r, "date", part="quarter"), sample_rows)
    assert result[0]["date_quarter"] == "2"


def test_extract_bad_value_uses_default(sample_rows):
    result = apply(
        lambda r: extract_date_part(r, "date", part="year", default="?"), sample_rows
    )
    assert result[3]["date_year"] == "?"


def test_extract_custom_output_column(sample_rows):
    result = apply(
        lambda r: extract_date_part(r, "date", part="day", output_column="dom"), sample_rows
    )
    assert "dom" in result[0]
    assert result[0]["dom"] == "15"
