"""Integration tests: chaining date operations."""
import pytest
from csv_surgeon.dateparser import parse_date_column, format_date_column, extract_date_part


@pytest.fixture
def mixed_format_rows():
    return [
        {"id": "1", "created": "2024-01-10"},
        {"id": "2", "created": "15/03/2023"},
        {"id": "3", "created": "20230701"},
        {"id": "4", "created": ""},
    ]


def test_parse_then_extract_year(mixed_format_rows):
    parsed = list(parse_date_column(mixed_format_rows, "created", output_column="iso"))
    extracted = list(extract_date_part(parsed, "iso", part="year"))
    assert extracted[0]["iso_year"] == "2024"
    assert extracted[1]["iso_year"] == "2023"


def test_parse_then_format_preserves_row_count(mixed_format_rows):
    parsed = list(parse_date_column(mixed_format_rows, "created"))
    formatted = list(format_date_column(parsed, "created", output_format="%d/%m/%Y"))
    assert len(formatted) == len(mixed_format_rows)


def test_parse_then_extract_preserves_all_columns(mixed_format_rows):
    parsed = list(parse_date_column(mixed_format_rows, "created"))
    extracted = list(extract_date_part(parsed, "created", part="month"))
    assert "id" in extracted[0]
    assert "created" in extracted[0]
    assert "created_month" in extracted[0]


def test_empty_date_propagates_default_through_chain(mixed_format_rows):
    parsed = list(parse_date_column(mixed_format_rows, "created", default="1900-01-01"))
    extracted = list(extract_date_part(parsed, "created", part="year"))
    assert extracted[3]["created_year"] == "1900"


def test_full_pipeline_all_rows_have_quarter(mixed_format_rows):
    parsed = list(parse_date_column(mixed_format_rows, "created", default="2000-01-01"))
    result = list(extract_date_part(parsed, "created", part="quarter"))
    assert all("created_quarter" in r for r in result)
    assert all(r["created_quarter"] != "" for r in result)
