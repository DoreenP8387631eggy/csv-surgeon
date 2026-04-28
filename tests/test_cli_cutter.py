"""Tests for csv_surgeon/cli_cutter.py."""
import argparse
import csv
import io
import sys
import pytest

from csv_surgeon.cli_cutter import cmd_cut


def _make_args(**kwargs):
    defaults = {
        "column": "text",
        "mode": "chars",
        "start": 0,
        "end": None,
        "sep": None,
        "out_col": None,
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _make_csv(rows):
    buf = io.StringIO()
    if not rows:
        return buf
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    buf.seek(0)
    return buf


def _read(captured):
    return list(csv.DictReader(io.StringIO(captured)))


@pytest.fixture
def sample_csv(monkeypatch):
    rows = [
        {"id": "1", "text": "hello world"},
        {"id": "2", "text": "foo:bar:baz"},
    ]
    return _make_csv(rows)


def test_cmd_cut_chars_adds_sliced_value(sample_csv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    cmd_cut(_make_args(mode="chars", start=0, end=5))
    out = capsys.readouterr().out
    rows = _read(out)
    assert rows[0]["text"] == "hello"


def test_cmd_cut_chars_out_col_preserves_source(sample_csv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    cmd_cut(_make_args(mode="chars", start=0, end=3, out_col="short"))
    out = capsys.readouterr().out
    rows = _read(out)
    assert rows[0]["short"] == "hel"
    assert rows[0]["text"] == "hello world"


def test_cmd_cut_before_separator(sample_csv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    cmd_cut(_make_args(mode="before", sep=":"))
    out = capsys.readouterr().out
    rows = _read(out)
    assert rows[1]["text"] == "foo"


def test_cmd_cut_after_separator(sample_csv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    cmd_cut(_make_args(mode="after", sep=":"))
    out = capsys.readouterr().out
    rows = _read(out)
    assert rows[1]["text"] == "bar:baz"


def test_cmd_cut_words_first_word(sample_csv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    cmd_cut(_make_args(mode="words", start=0, end=1, sep=" "))
    out = capsys.readouterr().out
    rows = _read(out)
    assert rows[0]["text"] == "hello"


def test_cmd_cut_unknown_mode_exits(sample_csv, monkeypatch):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    args = _make_args(mode="invalid")
    with pytest.raises(SystemExit):
        cmd_cut(args)


def test_cmd_cut_preserves_other_columns(sample_csv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", sample_csv)
    cmd_cut(_make_args(mode="chars", start=0, end=3))
    out = capsys.readouterr().out
    rows = _read(out)
    assert rows[0]["id"] == "1"
