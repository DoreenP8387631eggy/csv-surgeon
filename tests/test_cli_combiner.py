"""Tests for csv_surgeon/cli_combiner.py"""

import argparse
import csv
import io
import pytest

from csv_surgeon.cli_combiner import cmd_combine


def _make_args(**kwargs):
    defaults = dict(
        input=None,
        output=io.StringIO(),
        columns=None,
        template=None,
        output_col="combined",
        separator=" ",
        default="",
        keep_empty=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _csv(content):
    return io.StringIO(content)


def _read(buf):
    buf.seek(0)
    return list(csv.DictReader(buf))


SAMPLE_CSV = "first,last,city\nAlice,Smith,London\nBob,Jones,\n"


def test_cmd_combine_template_adds_column():
    args = _make_args(input=_csv(SAMPLE_CSV), template="{first} {last}")
    cmd_combine(args)
    rows = _read(args.output)
    assert "combined" in rows[0]


def test_cmd_combine_template_correct_value():
    args = _make_args(input=_csv(SAMPLE_CSV), template="{first} {last}")
    cmd_combine(args)
    rows = _read(args.output)
    assert rows[0]["combined"] == "Alice Smith"


def test_cmd_combine_columns_adds_column():
    args = _make_args(input=_csv(SAMPLE_CSV), columns=["first", "last"])
    cmd_combine(args)
    rows = _read(args.output)
    assert "combined" in rows[0]


def test_cmd_combine_columns_skips_empty():
    args = _make_args(input=_csv(SAMPLE_CSV), columns=["first", "city"])
    cmd_combine(args)
    rows = _read(args.output)
    # Bob has empty city
    assert rows[1]["combined"] == "Bob"


def test_cmd_combine_no_template_or_columns_exits(capsys):
    args = _make_args(input=_csv(SAMPLE_CSV))
    with pytest.raises(SystemExit):
        cmd_combine(args)
