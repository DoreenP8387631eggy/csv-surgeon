"""Tests for csv_surgeon.cli_merger."""
import argparse
import io
import sys
import pytest
from unittest.mock import patch, MagicMock
from csv_surgeon.cli_merger import cmd_merge, register


def _make_args(**kwargs):
    defaults = {"inputs": [], "output": "-", "strict": False, "fill": ""}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


@pytest.fixture
def csv_a(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("id,name\n1,Alice\n2,Bob\n")
    return str(p)


@pytest.fixture
def csv_b(tmp_path):
    p = tmp_path / "b.csv"
    p.write_text("id,name\n3,Carol\n")
    return str(p)


@pytest.fixture
def csv_extra(tmp_path):
    p = tmp_path / "extra.csv"
    p.write_text("id,name,age\n4,Dave,25\n")
    return str(p)


def test_merge_requires_at_least_two_inputs():
    args = _make_args(inputs=["only_one.csv"])
    with pytest.raises(SystemExit) as exc_info:
        cmd_merge(args)
    assert exc_info.value.code == 1


def test_merge_produces_combined_output(csv_a, csv_b, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(inputs=[csv_a, csv_b], output=out)
    cmd_merge(args)
    content = open(out).read()
    assert "Alice" in content
    assert "Carol" in content


def test_merge_strict_raises_on_mismatch(csv_a, csv_extra, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(inputs=[csv_a, csv_extra], output=out, strict=True)
    with pytest.raises(SystemExit) as exc_info:
        cmd_merge(args)
    assert exc_info.value.code == 1


def test_merge_fill_value_used(csv_a, csv_extra, tmp_path):
    out = str(tmp_path / "out.csv")
    args = _make_args(inputs=[csv_a, csv_extra], output=out, fill="N/A")
    cmd_merge(args)
    content = open(out).read()
    assert "N/A" in content


def test_register_adds_merge_subcommand():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    parsed = parser.parse_args(["merge", "a.csv", "b.csv"])
    assert parsed.inputs == ["a.csv", "b.csv"]
    assert parsed.strict is False
    assert parsed.fill == ""


def test_register_strict_flag():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    register(subparsers)
    parsed = parser.parse_args(["merge", "a.csv", "b.csv", "--strict"])
    assert parsed.strict is True
