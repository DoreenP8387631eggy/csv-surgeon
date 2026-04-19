"""Integration tests combining sequencer with other pipeline steps."""
from csv_surgeon.sequencer import sequence_column, cycle_column, alpha_sequence_column
from csv_surgeon.filters import equals
from csv_surgeon.pipeline import FilterPipeline


def _make_rows(n=6):
    return [{"name": f"user{i}", "score": str(i * 10)} for i in range(1, n + 1)]


def test_sequence_then_filter_by_id():
    rows = _make_rows(5)
    sequenced = list(sequence_column(iter(rows), "id"))
    pipeline = FilterPipeline()
    pipeline.add_filter(equals("id", "3"))
    result = [r for r in sequenced if pipeline._row_passes(r)]
    assert len(result) == 1
    assert result[0]["name"] == "user3"


def test_cycle_then_filter_group():
    rows = _make_rows(6)
    cycled = list(cycle_column(iter(rows), "group", ["A", "B", "C"]))
    pipeline = FilterPipeline()
    pipeline.add_filter(equals("group", "A"))
    result = [r for r in cycled if pipeline._row_passes(r)]
    assert len(result) == 2


def test_sequence_preserves_all_rows():
    rows = _make_rows(10)
    result = list(sequence_column(iter(rows), "seq"))
    assert len(result) == 10


def test_alpha_sequence_all_unique():
    rows = _make_rows(5)
    result = list(alpha_sequence_column(iter(rows), "code", prefix="ID-", pad=3))
    codes = [r["code"] for r in result]
    assert len(set(codes)) == 5


def test_sequence_then_alpha_both_present():
    rows = _make_rows(3)
    step1 = sequence_column(iter(rows), "num_id")
    step2 = list(alpha_sequence_column(step1, "str_id", prefix="R"))
    assert all("num_id" in r and "str_id" in r for r in step2)
    assert step2[0]["num_id"] == "1"
    assert step2[0]["str_id"] == "R1"
