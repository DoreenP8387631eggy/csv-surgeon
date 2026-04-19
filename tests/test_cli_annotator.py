import argparse
import io
import csv
import pytest
from csv_surgeon.cli_annotator import cmd_annotate


def _make_args(**kwargs):
    defaults = dict(
        mode="row_number",
        output_col="_row_num",
        start=1,
        source="",
        columns=None,
        algorithm="md5",
        column=None,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _sample_csv():
    return io.StringIO("name,score\nAlice,90\nBob,\nCarol,75\n")


def _read(buf):
    buf.seek(0)
    return list(csv.DictReader(buf))


def test_row_number_adds_column():
    out = io.StringIO()
    args = _make_args(input=_sample_csv(), output=out, mode="row_number", output_col="_row_num")
    cmd_annotate(args)
    rows = _read(out)
    assert all("_row_num" in r for r in rows)


def test_row_number_correct_sequence():
    out = io.StringIO()
    args = _make_args(input=_sample_csv(), output=out, mode="row_number", output_col="_row_num")
    cmd_annotate(args)
    rows = _read(out)
    assert [r["_row_num"] for r in rows] == ["1", "2", "3"]


def test_source_mode_tags_rows():
    out = io.StringIO()
    args = _make_args(input=_sample_csv(), output=out, mode="source", source="test.csv", output_col="_source")
    cmd_annotate(args)
    rows = _read(out)
    assert all(r["_source"] == "test.csv" for r in rows)


def test_hash_mode_adds_column():
    out = io.StringIO()
    args = _make_args(input=_sample_csv(), output=out, mode="hash", output_col="_hash")
    cmd_annotate(args)
    rows = _read(out)
    assert all("_hash" in r for r in rows)


def test_is_empty_mode_flags_blank():
    out = io.StringIO()
    args = _make_args(input=_sample_csv(), output=out, mode="is_empty", column="score", output_col="_is_empty")
    cmd_annotate(args)
    rows = _read(out)
    assert rows[1]["_is_empty"] == "true"
    assert rows[0]["_is_empty"] == "false"


def test_is_empty_requires_column(capsys):
    out = io.StringIO()
    args = _make_args(input=_sample_csv(), output=out, mode="is_empty", column=None, output_col="_is_empty")
    with pytest.raises(SystemExit):
        cmd_annotate(args)
