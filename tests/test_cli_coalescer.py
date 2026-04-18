import io
import csv
import argparse
import pytest
from unittest.mock import patch
from csv_surgeon.cli_coalescer import cmd_coalesce


def _make_args(**kwargs):
    defaults = {
        "columns": ["a", "b", "c"],
        "output": "result",
        "default": "",
        "fill": False,
        "output_file": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def sample_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("a,b,c\n,second,third\nfirst,second,third\n,,only_c\n")
    return str(p)


def _read(captured: io.StringIO):
    captured.seek(0)
    return list(csv.DictReader(captured))


def test_cmd_coalesce_adds_output_column(sample_csv):
    out = io.StringIO()
    args = _make_args(input=sample_csv)
    with patch("csv_surgeon.cli_coalescer.StreamingCSVWriter") as MockWriter:
        instance = MockWriter.return_value
        written = []
        instance.write_rows.side_effect = lambda rows: written.extend(list(rows))
        cmd_coalesce(args)
    assert all("result" in row for row in written)


def test_cmd_coalesce_correct_values(sample_csv):
    out = io.StringIO()
    args = _make_args(input=sample_csv)
    with patch("csv_surgeon.cli_coalescer.StreamingCSVWriter") as MockWriter:
        instance = MockWriter.return_value
        written = []
        instance.write_rows.side_effect = lambda rows: written.extend(list(rows))
        cmd_coalesce(args)
    assert written[0]["result"] == "second"
    assert written[1]["result"] == "first"
    assert written[2]["result"] == "only_c"


def test_cmd_coalesce_fill_mode(sample_csv):
    args = _make_args(input=sample_csv, columns=["a", "b"], fill=True)
    with patch("csv_surgeon.cli_coalescer.StreamingCSVWriter") as MockWriter:
        instance = MockWriter.return_value
        written = []
        instance.write_rows.side_effect = lambda rows: written.extend(list(rows))
        cmd_coalesce(args)
    assert written[0]["a"] == "second"
    assert written[1]["a"] == "first"


def test_cmd_coalesce_default_value(tmp_path):
    p = tmp_path / "empty.csv"
    p.write_text("a,b\n,\n,\n")
    args = _make_args(input=str(p), columns=["a", "b"], default="MISSING")
    with patch("csv_surgeon.cli_coalescer.StreamingCSVWriter") as MockWriter:
        instance = MockWriter.return_value
        written = []
        instance.write_rows.side_effect = lambda rows: written.extend(list(rows))
        cmd_coalesce(args)
    assert all(row["result"] == "MISSING" for row in written)
