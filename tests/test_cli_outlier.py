import argparse
import io
import csv
import pytest
from csv_surgeon.cli_outlier import cmd_outlier


def _make_args(csv_text: str, method="zscore", column="val",
               threshold=2.0, multiplier=1.5, output_col="is_outlier"):
    ns = argparse.Namespace(
        input=io.StringIO(csv_text),
        output=io.StringIO(),
        column=column,
        method=method,
        threshold=threshold,
        multiplier=multiplier,
        output_col=output_col,
    )
    return ns


SAMPLE = "val\n10\n11\n12\n10\n11\n100\n"


def _read(args):
    args.output.seek(0)
    return list(csv.DictReader(args.output))


def test_zscore_adds_flag_column():
    args = _make_args(SAMPLE)
    cmd_outlier(args)
    rows = _read(args)
    assert "is_outlier" in rows[0]


def test_zscore_flags_last_row():
    args = _make_args(SAMPLE)
    cmd_outlier(args)
    rows = _read(args)
    assert rows[-1]["is_outlier"] == "true"


def test_iqr_method_runs():
    args = _make_args(SAMPLE, method="iqr")
    cmd_outlier(args)
    rows = _read(args)
    assert len(rows) == 6


def test_custom_output_col():
    args = _make_args(SAMPLE, output_col="flag")
    cmd_outlier(args)
    rows = _read(args)
    assert "flag" in rows[0]


def test_invalid_method_exits(capsys):
    args = _make_args(SAMPLE, method="bad")
    with pytest.raises(SystemExit):
        cmd_outlier(args)
