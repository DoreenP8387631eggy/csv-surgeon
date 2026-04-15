"""Tests for csv_surgeon.cli_pivotter (CLI pivot/melt commands)."""
import argparse
import io
import pytest
from unittest.mock import patch, MagicMock
from csv_surgeon.cli_pivotter import cmd_pivot, cmd_melt, register


def _make_pivot_args(**kwargs):
    defaults = {
        "input": "in.csv",
        "output": "out.csv",
        "index_col": "region",
        "pivot_col": "product",
        "value_col": "sales",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_melt_args(**kwargs):
    defaults = {
        "input": "in.csv",
        "output": "out.csv",
        "id_cols": "id,name",
        "value_cols": "jan,feb",
        "var_name": "variable",
        "value_name": "value",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


SALES_CSV = "region,product,sales\nnorth,apples,100\nnorth,bananas,200\nsouth,apples,150\n"
WIDE_CSV = "id,name,jan,feb\n1,Alice,10,20\n2,Bob,30,40\n"


@pytest.fixture
def sales_csv(tmp_path):
    f = tmp_path / "sales.csv"
    f.write_text(SALES_CSV)
    return str(f)


@pytest.fixture
def wide_csv(tmp_path):
    f = tmp_path / "wide.csv"
    f.write_text(WIDE_CSV)
    return str(f)


def test_cmd_pivot_creates_output(sales_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_pivot_args(input=sales_csv, output=out)
    cmd_pivot(args)
    content = open(out).read()
    assert "region" in content
    assert "apples" in content


def test_cmd_pivot_correct_values(sales_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_pivot_args(input=sales_csv, output=out)
    cmd_pivot(args)
    content = open(out).read()
    assert "100" in content
    assert "200" in content


def test_cmd_pivot_empty_input_exits(tmp_path):
    empty = tmp_path / "empty.csv"
    empty.write_text("region,product,sales\n")
    out = str(tmp_path / "out.csv")
    args = _make_pivot_args(input=str(empty), output=out)
    with pytest.raises(SystemExit):
        cmd_pivot(args)


def test_cmd_melt_creates_output(wide_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_melt_args(input=wide_csv, output=out)
    cmd_melt(args)
    content = open(out).read()
    assert "variable" in content
    assert "value" in content


def test_cmd_melt_row_count(wide_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_melt_args(input=wide_csv, output=out)
    cmd_melt(args)
    lines = [l for l in open(out).read().splitlines() if l.strip()]
    # header + 4 data rows (2 ids x 2 value cols)
    assert len(lines) == 5


def test_cmd_melt_auto_value_cols(wide_csv, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_melt_args(input=wide_csv, output=out, value_cols=None)
    cmd_melt(args)
    content = open(out).read()
    assert "jan" in content or "feb" in content


def test_register_adds_pivot_and_melt_subcommands():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    args = parser.parse_args(["pivot", "in.csv", "out.csv",
                               "--index-col", "r", "--pivot-col", "p", "--value-col", "v"])
    assert args.func == cmd_pivot
