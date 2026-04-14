"""Tests for the StreamingCSVReader module."""

import csv
import os
import tempfile

import pytest

from csv_surgeon.reader import StreamingCSVReader


SAMPLE_ROWS = [
    {"name": "Alice", "age": "30", "city": "New York"},
    {"name": "Bob", "age": "25", "city": "London"},
    {"name": "Carol", "age": "35", "city": "Berlin"},
]


@pytest.fixture()
def sample_csv(tmp_path):
    """Write a small CSV file and return its path."""
    path = tmp_path / "sample.csv"
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["name", "age", "city"])
        writer.writeheader()
        writer.writerows(SAMPLE_ROWS)
    return str(path)


@pytest.fixture()
def csv_with_blank_lines(tmp_path):
    """Write a CSV that contains blank lines between data rows."""
    path = tmp_path / "blanks.csv"
    path.write_text("name,age\nAlice,30\n,,\nBob,25\n", encoding="utf-8")
    return str(path)


def test_iter_rows_returns_all_data_rows(sample_csv):
    reader = StreamingCSVReader(sample_csv)
    rows = list(reader.iter_rows())
    assert len(rows) == 3


def test_iter_rows_correct_values(sample_csv):
    reader = StreamingCSVReader(sample_csv)
    rows = list(reader.iter_rows())
    assert rows[0]["name"] == "Alice"
    assert rows[1]["city"] == "London"
    assert rows[2]["age"] == "35"


def test_headers_populated_after_iter(sample_csv):
    reader = StreamingCSVReader(sample_csv)
    list(reader.iter_rows())
    assert reader.headers == ["name", "age", "city"]


def test_peek_headers_does_not_read_data(sample_csv):
    reader = StreamingCSVReader(sample_csv)
    headers = reader.peek_headers()
    assert headers == ["name", "age", "city"]


def test_iter_raw_rows_includes_header(sample_csv):
    reader = StreamingCSVReader(sample_csv)
    raw = list(reader.iter_raw_rows())
    assert raw[0] == ["name", "age", "city"]
    assert len(raw) == 4  # header + 3 data rows


def test_blank_lines_skipped_by_default(csv_with_blank_lines):
    reader = StreamingCSVReader(csv_with_blank_lines)
    rows = list(reader.iter_rows())
    assert len(rows) == 2


def test_blank_lines_included_when_disabled(csv_with_blank_lines):
    reader = StreamingCSVReader(csv_with_blank_lines, skip_blank_lines=False)
    rows = list(reader.iter_rows())
    assert len(rows) == 3


def test_custom_delimiter(tmp_path):
    path = tmp_path / "pipe.csv"
    path.write_text("name|age\nDave|40\n", encoding="utf-8")
    reader = StreamingCSVReader(str(path), delimiter="|")
    rows = list(reader.iter_rows())
    assert rows[0]["name"] == "Dave"
    assert rows[0]["age"] == "40"
