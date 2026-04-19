import io
import csv
import argparse
import pytest
from csv_surgeon.cli_scaler import cmd_scale


def _make_args(csv_content: str, column: str, method: str = "minmax",
               output_column: str = "", range_=(0.0, 1.0)):
    args = argparse.Namespace()
    args.input = io.StringIO(csv_content)
    args.output = io.StringIO()
    args.column = column
    args.method = method
    args.output_column = output_column
    args.range = list(range_)
    return args


def _read(args):
    args.output.seek(0)
    return list(csv.DictReader(args.output))


SAMPLE = "name,score\na,10\nb,20\nc,30\n"


def test_minmax_adds_scaled_column():
    args = _make_args(SAMPLE, column="score", output_column="scaled")
    cmd_scale(args)
    rows = _read(args)
    assert "scaled" in rows[0]


def test_minmax_first_value_is_zero():
    args = _make_args(SAMPLE, column="score")
    cmd_scale(args)
    rows = _read(args)
    assert float(rows[0]["score"]) == pytest.approx(0.0)


def test_minmax_last_value_is_one():
    args = _make_args(SAMPLE, column="score")
    cmd_scale(args)
    rows = _read(args)
    assert float(rows[-1]["score"]) == pytest.approx(1.0)


def test_zscore_method_runs():
    args = _make_args(SAMPLE, column="score", method="zscore")
    cmd_scale(args)
    rows = _read(args)
    assert len(rows) == 3


def test_robust_method_runs():
    args = _make_args(SAMPLE, column="score", method="robust")
    cmd_scale(args)
    rows = _read(args)
    assert len(rows) == 3


def test_preserves_other_columns():
    args = _make_args(SAMPLE, column="score")
    cmd_scale(args)
    rows = _read(args)
    assert rows[0]["name"] == "a"


def test_custom_range():
    args = _make_args(SAMPLE, column="score", range_=(-1.0, 1.0))
    cmd_scale(args)
    rows = _read(args)
    assert float(rows[0]["score"]) == pytest.approx(-1.0)
    assert float(rows[-1]["score"]) == pytest.approx(1.0)
