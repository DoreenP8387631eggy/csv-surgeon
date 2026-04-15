"""Integration-style tests for the validate CLI sub-command."""

import io
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from csv_surgeon.cli_validator import cmd_validate, register


def _make_args(**kwargs):
    defaults = {
        "input": None,
        "required": None,
        "numeric": None,
        "max_length": None,
        "one_of": None,
        "strict": False,
    }
    defaults.update(kwargs)
    ns = types.SimpleNamespace(**defaults)
    return ns


@pytest.fixture()
def valid_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,role\nAlice,30,admin\nBob,25,user\n")
    return str(p)


@pytest.fixture()
def invalid_csv(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("name,age,role\n,abc,superadmin\nBob,25,user\n")
    return str(p)


def test_no_validators_exits_with_error(valid_csv, capsys):
    args = _make_args(input=valid_csv)
    with pytest.raises(SystemExit) as exc_info:
        cmd_validate(args)
    assert exc_info.value.code == 1


def test_valid_file_reports_zero_errors(valid_csv, capsys):
    args = _make_args(input=valid_csv, required=["name"], numeric=["age"])
    cmd_validate(args)
    captured = capsys.readouterr()
    assert "0 invalid" in captured.err


def test_invalid_file_reports_errors(invalid_csv, capsys):
    args = _make_args(
        input=invalid_csv,
        required=["name"],
        numeric=["age"],
    )
    cmd_validate(args)
    captured = capsys.readouterr()
    assert "2 invalid" in captured.err or "1 invalid" in captured.err


def test_strict_mode_exits_nonzero_on_errors(invalid_csv, capsys):
    args = _make_args(input=invalid_csv, required=["name"], strict=True)
    with pytest.raises(SystemExit) as exc_info:
        cmd_validate(args)
    assert exc_info.value.code == 2


def test_strict_mode_no_exit_when_valid(valid_csv, capsys):
    args = _make_args(input=valid_csv, required=["name"], strict=True)
    # Should not raise
    cmd_validate(args)


def test_max_length_validator_via_cli(tmp_path, capsys):
    p = tmp_path / "data.csv"
    p.write_text("name,age\nAlexandria,30\nBob,25\n")
    args = _make_args(input=str(p), max_length=["name:5"])
    cmd_validate(args)
    captured = capsys.readouterr()
    assert "1 invalid" in captured.err


def test_one_of_validator_via_cli(tmp_path, capsys):
    p = tmp_path / "data.csv"
    p.write_text("name,role\nAlice,superadmin\nBob,user\n")
    args = _make_args(input=str(p), one_of=["role:admin,user"])
    cmd_validate(args)
    captured = capsys.readouterr()
    assert "1 invalid" in captured.err


def test_register_adds_validate_subcommand():
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    args = parser.parse_args(["validate", "file.csv", "--required", "name"])
    assert args.input == "file.csv"
    assert args.required == ["name"]
