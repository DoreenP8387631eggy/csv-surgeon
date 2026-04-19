import pytest
from csv_surgeon.annotator import (
    annotate_row_number,
    annotate_source,
    annotate_hash,
    annotate_is_empty,
)


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "score": "90"},
        {"name": "Bob", "score": ""},
        {"name": "Carol", "score": "75"},
    ]


def test_annotate_row_number_adds_column(sample_rows):
    result = list(annotate_row_number(sample_rows))
    assert all("_row_num" in r for r in result)


def test_annotate_row_number_correct_values(sample_rows):
    result = list(annotate_row_number(sample_rows))
    assert [r["_row_num"] for r in result] == ["1", "2", "3"]


def test_annotate_row_number_custom_start(sample_rows):
    result = list(annotate_row_number(sample_rows, start=0))
    assert result[0]["_row_num"] == "0"


def test_annotate_row_number_custom_col(sample_rows):
    result = list(annotate_row_number(sample_rows, output_col="idx"))
    assert "idx" in result[0]


def test_annotate_source_adds_label(sample_rows):
    result = list(annotate_source(sample_rows, source="file_a.csv"))
    assert all(r["_source"] == "file_a.csv" for r in result)


def test_annotate_source_custom_col(sample_rows):
    result = list(annotate_source(sample_rows, source="x", output_col="origin"))
    assert "origin" in result[0]


def test_annotate_source_preserves_fields(sample_rows):
    result = list(annotate_source(sample_rows, source="s"))
    assert result[0]["name"] == "Alice"


def test_annotate_hash_adds_column(sample_rows):
    result = list(annotate_hash(sample_rows))
    assert all("_hash" in r for r in result)


def test_annotate_hash_deterministic(sample_rows):
    r1 = list(annotate_hash(sample_rows))
    r2 = list(annotate_hash(sample_rows))
    assert r1[0]["_hash"] == r2[0]["_hash"]


def test_annotate_hash_different_rows_differ(sample_rows):
    result = list(annotate_hash(sample_rows))
    assert result[0]["_hash"] != result[1]["_hash"]


def test_annotate_hash_subset_columns(sample_rows):
    result = list(annotate_hash(sample_rows, columns=["name"]))
    assert len(result[0]["_hash"]) == 32  # md5 hex


def test_annotate_is_empty_false_for_non_empty(sample_rows):
    result = list(annotate_is_empty(sample_rows, column="score"))
    assert result[0]["_is_empty"] == "false"


def test_annotate_is_empty_true_for_empty(sample_rows):
    result = list(annotate_is_empty(sample_rows, column="score"))
    assert result[1]["_is_empty"] == "true"


def test_annotate_is_empty_missing_column(sample_rows):
    result = list(annotate_is_empty(sample_rows, column="nonexistent"))
    assert all(r["_is_empty"] == "true" for r in result)


def test_annotate_is_empty_custom_col(sample_rows):
    result = list(annotate_is_empty(sample_rows, column="score", output_col="blank"))
    assert "blank" in result[0]
