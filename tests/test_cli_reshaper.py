import io
import csv
import pytest
import argparse
from csv_surgeon.cli_reshaper import cmd_reshape


CSV_DATA = "a,b,c\n1,2,3\n4,5,6\n"


def _make_args(**kwargs):
    defaults = dict(input=io.StringIO(CSV_DATA), output=io.StringIO())
    defaults.update(kwargs)
    ns = argparse.Namespace(**defaults)
    if not hasattr(ns, "select"):
        ns.select = None
    if not hasattr(ns, "drop"):
        ns.drop = None
    if not hasattr(ns, "order"):
        ns.order = None
    return ns


def _read(output: io.StringIO):
    output.seek(0)
    return list(csv.DictReader(output))


def test_select_keeps_only_specified_columns():
    args = _make_args(select="a,c")
    cmd_reshape(args)
    rows = _read(args.output)
    assert list(rows[0].keys()) == ["a", "c"]


def test_select_preserves_values():
    args = _make_args(select="a,b")
    cmd_reshape(args)
    rows = _read(args.output)
    assert rows[0]["a"] == "1"
    assert rows[1]["b"] == "5"


def test_drop_removes_column():
    args = _make_args(drop="b")
    cmd_reshape(args)
    rows = _read(args.output)
    assert "b" not in rows[0]
    assert "a" in rows[0]
    assert "c" in rows[0]


def test_order_reorders_columns():
    args = _make_args(order="c,b,a")
    cmd_reshape(args)
    rows = _read(args.output)
    assert list(rows[0].keys()) == ["c", "b", "a"]


def test_no_option_exits(capsys):
    args = _make_args()
    with pytest.raises(SystemExit):
        cmd_reshape(args)


def test_select_row_count_preserved():
    args = _make_args(select="a")
    cmd_reshape(args)
    rows = _read(args.output)
    assert len(rows) == 2
