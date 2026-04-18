import argparse
import io
import csv
import pytest
from csv_surgeon.cli_bucketer import cmd_bucket


def _make_args(csv_text, edges, labels=None, column="score", output_column="bucket", default=""):
    ns = argparse.Namespace(
        input=io.StringIO(csv_text),
        output=io.StringIO(),
        column=column,
        edges=edges,
        labels=labels,
        output_column=output_column,
        default=default,
    )
    return ns


def _read(args):
    args.output.seek(0)
    return list(csv.DictReader(args.output))


SAMPLE = "name,score\nAlice,15\nBob,55\nCarol,85\n"


def test_cmd_bucket_adds_bucket_column():
    args = _make_args(SAMPLE, "0,33,66,100", labels="low,mid,high")
    cmd_bucket(args)
    rows = _read(args)
    assert "bucket" in rows[0]


def test_cmd_bucket_correct_labels():
    args = _make_args(SAMPLE, "0,33,66,100", labels="low,mid,high")
    cmd_bucket(args)
    rows = _read(args)
    assert rows[0]["bucket"] == "low"
    assert rows[1]["bucket"] == "mid"
    assert rows[2]["bucket"] == "high"


def test_cmd_bucket_custom_output_column():
    args = _make_args(SAMPLE, "0,100", labels="all", output_column="tier")
    cmd_bucket(args)
    rows = _read(args)
    assert "tier" in rows[0]


def test_cmd_bucket_empty_input_produces_no_output():
    args = _make_args("name,score\n", "0,100", labels="all")
    cmd_bucket(args)
    args.output.seek(0)
    assert args.output.read().strip() == ""


def test_cmd_bucket_preserves_other_columns():
    args = _make_args(SAMPLE, "0,100", labels="all")
    cmd_bucket(args)
    rows = _read(args)
    assert rows[0]["name"] == "Alice"
