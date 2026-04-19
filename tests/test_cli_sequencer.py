import csv
import io
import argparse
import pytest
from csv_surgeon.cli_sequencer import cmd_sequence


def _make_args(**kwargs):
    defaults = {
        "col": "id",
        "mode": "int",
        "start": 1,
        "step": 1,
        "prefix": "",
        "pad": 0,
        "values": [],
        "value": "",
        "overwrite": False,
    }
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


def test_cmd_sequence_int_adds_column():
    src = _make_csv([{"name": "A"}, {"name": "B"}])
    out = io.StringIO()
    args = _make_args(input=src, output=out, col="id", mode="int")
    cmd_sequence(args)
    rows = _read(out)
    assert "id" in rows[0]


def test_cmd_sequence_int_correct_values():
    src = _make_csv([{"name": "A"}, {"name": "B"}, {"name": "C"}])
    out = io.StringIO()
    args = _make_args(input=src, output=out, col="id", mode="int")
    cmd_sequence(args)
    rows = _read(out)
    assert [r["id"] for r in rows] == ["1", "2", "3"]


def test_cmd_sequence_alpha_prefix():
    src = _make_csv([{"name": "A"}, {"name": "B"}])
    out = io.StringIO()
    args = _make_args(input=src, output=out, col="code", mode="alpha", prefix="ROW-", pad=0)
    cmd_sequence(args)
    rows = _read(out)
    assert rows[0]["code"] == "ROW-1"


def test_cmd_sequence_cycle():
    src = _make_csv([{"name": "A"}, {"name": "B"}, {"name": "C"}])
    out = io.StringIO()
    args = _make_args(input=src, output=out, col="grp", mode="cycle", values=["X", "Y"])
    cmd_sequence(args)
    rows = _read(out)
    assert [r["grp"] for r in rows] == ["X", "Y", "X"]


def test_cmd_sequence_repeat():
    src = _make_csv([{"name": "A"}, {"name": "B"}])
    out = io.StringIO()
    args = _make_args(input=src, output=out, col="src", mode="repeat", value="batch1")
    cmd_sequence(args)
    rows = _read(out)
    assert all(r["src"] == "batch1" for r in rows)


def test_cmd_sequence_empty_input():
    src = io.StringIO("name\n")
    out = io.StringIO()
    args = _make_args(input=src, output=out, col="id", mode="int")
    cmd_sequence(args)  # should not raise
