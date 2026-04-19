import io
import csv
import argparse
import pytest
from csv_surgeon.cli_extractor import cmd_extract


def _make_args(**kwargs):
    defaults = dict(
        column="text",
        pattern=r"#\d+",
        mode="pattern",
        output_col=None,
        group=0,
        separator="|",
        default="",
        start="",
        end="",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_csv(rows):
    buf = io.StringIO()
    if rows:
        w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    buf.seek(0)
    return buf


def _read(output_buf):
    output_buf.seek(0)
    return list(csv.DictReader(output_buf))


def test_cmd_extract_pattern_adds_column():
    inp = _make_csv([{"text": "Order #42 done"}])
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="pattern", pattern=r"#\d+")
    cmd_extract(args)
    rows = _read(out)
    assert "text_extracted" in rows[0]


def test_cmd_extract_pattern_correct_value():
    inp = _make_csv([{"text": "ref: ABC-999"}])
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="pattern", pattern=r"[A-Z]+-\d+")
    cmd_extract(args)
    rows = _read(out)
    assert rows[0]["text_extracted"] == "ABC-999"


def test_cmd_extract_all_joins_matches():
    inp = _make_csv([{"text": "#1 and #2 and #3"}])
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="all", pattern=r"#\d+", separator=",")
    cmd_extract(args)
    rows = _read(out)
    assert rows[0]["text_all"] == "#1,#2,#3"


def test_cmd_extract_between_extracts_inner():
    inp = _make_csv([{"text": "[hello world]"}])
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="between", start="[", end="]")
    cmd_extract(args)
    rows = _read(out)
    assert rows[0]["text_between"] == "hello world"


def test_cmd_extract_named_groups():
    inp = _make_csv([{"text": "age: 25"}])
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="named", pattern=r"age: (?P<age>\d+)")
    cmd_extract(args)
    rows = _read(out)
    assert rows[0]["age"] == "25"
