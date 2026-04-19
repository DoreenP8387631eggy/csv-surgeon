import csv
import io
import pytest
from types import SimpleNamespace
from unittest.mock import patch, mock_open
from csv_surgeon.cli_linker import cmd_link


def _csv(rows):
    buf = io.StringIO()
    if rows:
        w = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return buf.getvalue()


def _make_args(**kwargs):
    defaults = dict(
        left="left.csv", right="right.csv",
        left_key="id", right_key="user_id",
        mode="exists", right_col="",
        output_col="linked", default="",
        separator="|", output="",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


LEFT = [{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}, {"id": "3", "name": "": "1", "tagtag": "viewer"}]


def _read(capsys):
    captured = capsys.readouterr()
    return list(csv.DictReader(io.StringIO(captured.out)))


def test_exists_mode_adds_column(capsys):
    with patch("csv_surgeon.cli_linker._read_rows", side_effect=[LEFT, RIGHT]):
        cmd_link(_make_args(mode="exists"))
    rows = _read(capsys)
    assert "linked" in rows[0]


def test_exists_mode_true_for_match(capsys):
    with patch("csv_surgeon.cli_linker._read_rows", side_effect=[LEFT, RIGHT]):
        cmd_link(_make_args(mode="exists"))
    rows = _read(capsys)
    assert rows[0]["linked"] == "true"
    assert rows[2]["linked"] == "false"


def test_count_mode_correct_values(capsys):
    with patch("csv_surgeon.cli_linker._read_rows", side_effect=[LEFT, RIGHT]):
        cmd_link(_make_args(mode="count", output_col="n"))
    rows = _read(capsys)
    assert rows[0]["n"] == "2"
    assert rows[1]["n"] == "1"
    assert rows[2]["n"] == "0"


def test_column_mode_joins_values(capsys):
    with patch("csv_surgeon.cli_linker._read_rows", side_effect=[LEFT, RIGHT]):
        cmd_link(_make_args(mode="column", right_col="tag", output_col="tags"))
    rows = _read(capsys)
    assert rows[0]["tags"] == "admin|editor"


def test_column_mode_missing_right_col_exits(capsys):
    with patch("csv_surgeon.cli_linker._read_rows", side_effect=[LEFT, RIGHT]):
        with pytest.raises(SystemExit):
            cmd_link(_make_args(mode="column", right_col=""))


def test_unknown_mode_exits(capsys):
    with patch("csv_surgeon.cli_linker._read_rows", side_effect=[LEFT, RIGHT]):
        with pytest.raises(SystemExit):
            cmd_link(_make_args(mode="unknown"))
