"""Tests for csv_surgeon.cli_censor.cmd_censor."""
import argparse
import io
import csv
import pytest

from csv_surgeon.cli_censor import cmd_censor


SAMPLE_CSV = "name,email,score\nAlice,alice@example.com,95\nBob,bob@example.com,42\n"


def _make_args(**kwargs) -> argparse.Namespace:
    defaults = dict(
        column="email",
        columns=[],
        pattern=None,
        replacement="***",
        input=io.StringIO(SAMPLE_CSV),
        output=io.StringIO(),
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _read(args: argparse.Namespace):
    args.output.seek(0)
    return list(csv.DictReader(args.output))


def test_cmd_censor_replaces_column()
    args = _make_args()
    cmd_censor(args)
    rows = _read(args)
    assert all(r["email"] == "***" for r in rows)


def test_cmd_censor_preserves_other_columns():
    args = _make_args()
    cmd_censor(args)
    rows = _read(args)
    assert rows[0]["name"] == "Alice"


def test_cmd_censor_custom_replacement():
    args = _make_args(replacement="[HIDDEN]")
    cmd_censor(args)
    rows = _read(args)
    assert rows[0]["email"] == "[HIDDEN]"


def test_cmd_censor_pattern_mode():
    args = _make_args(pattern=r"@.*")
    cmd_censor(args)
    rows = _read(args)
    assert rows[0]["email"] == "alice***"


def test_cmd_censor_multi_column_mode():
    args = _make_args(column="name", columns=["email"])
    cmd_censor(args)
    rows = _read(args)
    assert rows[0]["name"] == "***"
    assert rows[0]["email"] == "***"
    assert rows[0]["score"] == "95"
