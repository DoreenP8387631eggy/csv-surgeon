import argparse
import csv
import io
import pytest
from csv_surgeon.cli_scorer import cmd_score, register


CSV_DATA = "name,age,salary\nAlice,30,90000\nBob,25,50000\nCarol,40,120000\n"


def _make_args(**kwargs):
    defaults = dict(
        input=io.StringIO(CSV_DATA),
        output=io.StringIO(),
        rule=[],
        score_column="score",
        min_score=None,
        rank=False,
        ascending=False,
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _read_output(args):
    args.output.seek(0)
    return list(csv.DictReader(args.output))


def test_cmd_score_adds_score_column():
    args = _make_args(rule=["age:1"])
    cmd_score(args)
    rows = _read_output(args)
    assert all("score" in r for r in rows)


def test_cmd_score_correct_values():
    args = _make_args(rule=["age:1"])
    cmd_score(args)
    rows = _read_output(args)
    assert float(rows[0]["score"]) == pytest.approx(30.0)
    assert float(rows[1]["score"]) == pytest.approx(25.0)


def test_cmd_score_min_score_filters_rows():
    args = _make_args(rule=["age:1"], min_score=30.0)
    cmd_score(args)
    rows = _read_output(args)
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert "Bob" not in names


def test_cmd_score_rank_adds_rank_column():
    args = _make_args(rule=["salary:1"], rank=True)
    cmd_score(args)
    rows = _read_output(args)
    assert all("__rank__" in r for r in rows)


def test_cmd_score_rank_descending_order():
    args = _make_args(rule=["salary:1"], rank=True, ascending=False)
    cmd_score(args)
    rows = _read_output(args)
    assert rows[0]["name"] == "Carol"


def test_cmd_score_empty_rules_zero_scores():
    args = _make_args(rule=[])
    cmd_score(args)
    rows = _read_output(args)
    assert all(float(r["score"]) == 0.0 for r in rows)


def test_register_creates_score_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register(sub)
    ns = parser.parse_args(["score", "--rule", "age:1"])
    assert ns.rule == ["age:1"]
