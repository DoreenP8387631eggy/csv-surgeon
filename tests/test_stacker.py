"""Tests for csv_surgeon/stacker.py."""
import pytest
from csv_surgeon.stacker import stack_rows, unstack_rows


@pytest.fixture()
def wide_rows():
    return [
        {"id": "alice", "math": "90", "english": "85", "science": "92"},
        {"id": "bob",   "math": "78", "english": "88", "science": "74"},
    ]


@pytest.fixture()
def stacked_rows():
    return [
        {"id": "alice", "variable": "math",    "value": "90"},
        {"id": "alice", "variable": "english", "value": "85"},
        {"id": "alice", "variable": "science", "value": "92"},
        {"id": "bob",   "variable": "math",    "value": "78"},
        {"id": "bob",   "variable": "english", "value": "88"},
        {"id": "bob",   "variable": "science", "value": "74"},
    ]


# ---------------------------------------------------------------------------
# stack_rows
# ---------------------------------------------------------------------------

def test_stack_rows_produces_correct_count(wide_rows):
    result = list(stack_rows(iter(wide_rows), id_column="id"))
    # 2 people × 3 non-id columns = 6 rows
    assert len(result) == 6


def test_stack_rows_correct_keys(wide_rows):
    result = list(stack_rows(iter(wide_rows), id_column="id"))
    for row in result:
        assert set(row.keys()) == {"id", "variable", "value"}


def test_stack_rows_correct_values(wide_rows):
    result = list(stack_rows(iter(wide_rows), id_column="id"))
    alice_math = next(r for r in result if r["id"] == "alice" and r["variable"] == "math")
    assert alice_math["value"] == "90"


def test_stack_rows_custom_column_names(wide_rows):
    result = list(stack_rows(iter(wide_rows), id_column="id", var_name="col", value_name="val"))
    assert all("col" in r and "val" in r for r in result)


def test_stack_rows_empty_input():
    result = list(stack_rows(iter([]), id_column="id"))
    assert result == []


def test_stack_rows_single_column_beyond_id():
    rows = [{"id": "x", "score": "100"}]
    result = list(stack_rows(iter(rows), id_column="id"))
    assert len(result) == 1
    assert result[0] == {"id": "x", "variable": "score", "value": "100"}


# ---------------------------------------------------------------------------
# unstack_rows
# ---------------------------------------------------------------------------

def test_unstack_rows_produces_correct_count(stacked_rows):
    result = list(unstack_rows(iter(stacked_rows), id_column="id"))
    assert len(result) == 2


def test_unstack_rows_restores_columns(stacked_rows):
    result = list(unstack_rows(iter(stacked_rows), id_column="id"))
    assert set(result[0].keys()) == {"id", "math", "english", "science"}


def test_unstack_rows_correct_values(stacked_rows):
    result = list(unstack_rows(iter(stacked_rows), id_column="id"))
    alice = next(r for r in result if r["id"] == "alice")
    assert alice["math"] == "90"
    assert alice["english"] == "85"


def test_unstack_rows_fill_value_for_missing():
    rows = [
        {"id": "alice", "variable": "math",    "value": "90"},
        {"id": "bob",   "variable": "english", "value": "88"},
    ]
    result = list(unstack_rows(iter(rows), id_column="id", fill_value="N/A"))
    alice = next(r for r in result if r["id"] == "alice")
    bob   = next(r for r in result if r["id"] == "bob")
    assert alice["english"] == "N/A"
    assert bob["math"] == "N/A"


def test_unstack_rows_empty_input():
    result = list(unstack_rows(iter([]), id_column="id"))
    assert result == []


def test_stack_then_unstack_roundtrip(wide_rows):
    stacked   = list(stack_rows(iter(wide_rows), id_column="id"))
    unstacked = list(unstack_rows(iter(stacked), id_column="id"))
    assert len(unstacked) == len(wide_rows)
    for original, restored in zip(wide_rows, unstacked):
        assert original == restored
