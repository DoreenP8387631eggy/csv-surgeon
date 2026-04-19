import csv
import io
import pytest
from csv_surgeon.cli_cropper import cmd_crop


def _make_args(csv_text, operation, column, chars=None):
    class Args:
        pass
    a = Args()
    a.input = io.StringIO(csv_text)
    a.output = io.StringIO()
    a.operation = operation
    a.column = column
    a.chars = chars
    return a


def _read(args):
    args.output.seek(0)
    return list(csv.DictReader(args.output))


SAMPLE = "id,value\n1,  hello  \n2,  world  \n"


def test_strip_removes_whitespace():
    args = _make_args(SAMPLE, "strip", "value")
    cmd_crop(args)
    rows = _read(args)
    assert rows[0]["value"] == "hello"
    assert rows[1]["value"] == "world"


def test_lstrip_removes_leading_only():
    args = _make_args(SAMPLE, "lstrip", "value")
    cmd_crop(args)
    rows = _read(args)
    assert rows[0]["value"] == "hello  "


def test_rstrip_removes_trailing_only():
    args = _make_args(SAMPLE, "rstrip", "value")
    cmd_crop(args)
    rows = _read(args)
    assert rows[0]["value"] == "  hello"


def test_remove_prefix_strips_prefix():
    data = "id,code\n1,PRE_foo\n2,bar\n"
    args = _make_args(data, "remove-prefix", "code", chars="PRE_")
    cmd_crop(args)
    rows = _read(args)
    assert rows[0]["code"] == "foo"
    assert rows[1]["code"] == "bar"


def test_remove_suffix_strips_suffix():
    data = "id,code\n1,foo_SUF\n2,bar\n"
    args = _make_args(data, "remove-suffix", "code", chars="_SUF")
    cmd_crop(args)
    rows = _read(args)
    assert rows[0]["code"] == "foo"
    assert rows[1]["code"] == "bar"


def test_preserves_other_columns():
    args = _make_args(SAMPLE, "strip", "value")
    cmd_crop(args)
    rows = _read(args)
    assert rows[0]["id"] == "1"
