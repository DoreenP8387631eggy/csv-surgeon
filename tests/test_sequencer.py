import pytest
from csv_surgeon.sequencer import sequence_column, alpha_sequence_column, cycle_column, repeat_column


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "Bob", "score": "85"},
        {"name": "Carol", "score": "92"},
    ]


def test_sequence_column_adds_column(sample_rows):
    result = list(sequence_column(iter(sample_rows), "id"))
    assert all("id" in r for r in result)


def test_sequence_column_starts_at_one(sample_rows):
    result = list(sequence_column(iter(sample_rows), "id"))
    assert result[0]["id"] == "1"


def test_sequence_column_increments(sample_rows):
    result = list(sequence_column(iter(sample_rows), "id"))
    assert [r["id"] for r in result] == ["1", "2", "3"]


def test_sequence_column_custom_start(sample_rows):
    result = list(sequence_column(iter(sample_rows), "id", start=10))
    assert result[0]["id"] == "10"


def test_sequence_column_custom_step(sample_rows):
    result = list(sequence_column(iter(sample_rows), "id", step=5))
    assert [r["id"] for r in result] == ["1", "6", "11"]


def test_sequence_column_preserves_other_fields(sample_rows):
    result = list(sequence_column(iter(sample_rows), "id"))
    assert result[0]["name"] == "Alice"


def test_alpha_sequence_adds_prefix(sample_rows):
    result = list(alpha_sequence_column(iter(sample_rows), "code", prefix="ROW-"))
    assert result[0]["code"] == "ROW-1"


def test_alpha_sequence_zero_pad(sample_rows):
    result = list(alpha_sequence_column(iter(sample_rows), "code", pad=4))
    assert result[0]["code"] == "0001"


def test_alpha_sequence_prefix_and_pad(sample_rows):
    result = list(alpha_sequence_column(iter(sample_rows), "code", prefix="X", pad=3))
    assert result[1]["code"] == "X002"


def test_cycle_column_cycles_values(sample_rows):
    result = list(cycle_column(iter(sample_rows), "group", ["A", "B"]))
    assert [r["group"] for r in result] == ["A", "B", "A"]


def test_cycle_column_empty_values(sample_rows):
    result = list(cycle_column(iter(sample_rows), "group", []))
    assert all(r["group"] == "" for r in result)


def test_cycle_column_single_value(sample_rows):
    result = list(cycle_column(iter(sample_rows), "tag", ["yes"]))
    assert all(r["tag"] == "yes" for r in result)


def test_repeat_column_fills_constant(sample_rows):
    result = list(repeat_column(iter(sample_rows), "source", "import"))
    assert all(r["source"] == "import" for r in result)


def test_repeat_column_no_overwrite_keeps_existing():
    rows = [{"name": "Alice", "tag": "old"}, {"name": "Bob", "tag": ""}]
    result = list(repeat_column(iter(rows), "tag", "new", overwrite=False))
    assert result[0]["tag"] == "old"
    assert result[1]["tag"] == "new"


def test_sequence_empty_stream():
    result = list(sequence_column(iter([]), "id"))
    assert result == []
