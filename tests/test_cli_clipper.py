import csv
import io
import argparse
import pytest
from csv_surgeon.cli_clipper import cmd_clip


def _make_args(**kwargs):
    defaults = dict(
        column="score",
        mode="clamp",
        min=None,
        max=None,
        threshold=None,
        replacement="",
        output_column=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


SAMPLE_CSV = "name,score\nalice,5\nbob,150\ncarol,-10\n"


def _read(output: io.StringIO):
    output.seek(0)
    return list(csv.DictReader(output))


def test_clamp_max_limits_large_values():
    inp = io.StringIO(SAMPLE_CSV)
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="clamp", max="100")
    cmd_clip(args)
    rows = _read(out)
    assert rows[1]["score"] == "100"


def test_clamp_min_raises_negative_values():
    inp = io.StringIO(SAMPLE_CSV)
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="clamp", min="0")
    cmd_clip(args)
    rows = _read(out)
    assert rows[2]["score"] == "0"


def test_clip_below_replaces_value():
    inp = io.StringIO(SAMPLE_CSV)
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="below", threshold="0", replacement="N/A")
    cmd_clip(args)
    rows = _read(out)
    assert rows[2]["score"] == "N/A"


def test_clip_above_replaces_value():
    inp = io.StringIO(SAMPLE_CSV)
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="above", threshold="100", replacement="MAX")
    cmd_clip(args)
    rows = _read(out)
    assert rows[1]["score"] == "MAX"


def test_output_column_preserved_original():
    inp = io.StringIO(SAMPLE_CSV)
    out = io.StringIO()
    args = _make_args(input=inp, output=out, mode="clamp", max="100", output_column="clamped")
    cmd_clip(args)
    rows = _read(out)
    assert "clamped" in rows[0]
    assert rows[0]["score"] == "5"
