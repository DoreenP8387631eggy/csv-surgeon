import argparse
import io
import os
import csv
import pytest
from csv_surgeon.cli_partitioner import cmd_partition


def _make_args(csv_text: str, column: str, outdir: str) -> argparse.Namespace:
    return argparse.Namespace(
        input=io.StringIO(csv_text),
        column=column,
        outdir=outdir,
    )


SAMPLE = "region,sales\nnorth,100\nsouth,200\nnorth,150\n"


def test_cmd_partition_creates_files(tmp_path):
    args = _make_args(SAMPLE, "region", str(tmp_path / "out"))
    cmd_partition(args)
    files = os.listdir(tmp_path / "out")
    assert "north.csv" in files
    assert "south.csv" in files


def test_cmd_partition_correct_row_counts(tmp_path):
    args = _make_args(SAMPLE, "region", str(tmp_path / "out"))
    cmd_partition(args)
    with open(tmp_path / "out" / "north.csv") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2


def test_cmd_partition_preserves_values(tmp_path):
    args = _make_args(SAMPLE, "region", str(tmp_path / "out"))
    cmd_partition(args)
    with open(tmp_path / "out" / "south.csv") as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["sales"] == "200"


def test_cmd_partition_empty_value_uses_placeholder(tmp_path):
    data = "region,sales\n,100\nnorth,200\n"
    args = _make_args(data, "region", str(tmp_path / "out"))
    cmd_partition(args)
    files = os.listdir(tmp_path / "out")
    assert "__empty__.csv" in files


def test_cmd_partition_single_bucket(tmp_path):
    data = "region,sales\nnorth,100\nnorth,200\n"
    args = _make_args(data, "region", str(tmp_path / "out"))
    cmd_partition(args)
    files = os.listdir(tmp_path / "out")
    assert files == ["north.csv"]
