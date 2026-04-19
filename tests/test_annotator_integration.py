"""Integration tests: chain annotator transforms together."""
from csv_surgeon.annotator import (
    annotate_row_number,
    annotate_source,
    annotate_hash,
    annotate_is_empty,
)


def _make_rows():
    return [
        {"city": "London", "pop": "9000000"},
        {"city": "Paris", "pop": ""},
        {"city": "Berlin", "pop": "3700000"},
    ]


def test_chain_row_number_and_source():
    rows = _make_rows()
    result = list(annotate_source(annotate_row_number(rows), source="cities.csv"))
    assert result[0]["_row_num"] == "1"
    assert result[0]["_source"] == "cities.csv"


def test_chain_preserves_all_original_columns():
    rows = _make_rows()
    result = list(annotate_hash(annotate_row_number(rows)))
    assert all("city" in r and "pop" in r for r in result)


def test_chain_hash_is_unique_per_row():
    rows = _make_rows()
    result = list(annotate_hash(rows))
    hashes = [r["_hash"] for r in result]
    assert len(set(hashes)) == len(hashes)


def test_full_pipeline_all_annotations():
    rows = _make_rows()
    pipeline = annotate_is_empty(
        annotate_hash(
            annotate_source(
                annotate_row_number(rows, output_col="idx"),
                source="src",
            )
        ),
        column="pop",
        output_col="pop_empty",
    )
    result = list(pipeline)
    assert len(result) == 3
    assert result[1]["pop_empty"] == "true"
    assert result[0]["pop_empty"] == "false"
    assert "idx" in result[0]
    assert "_source" in result[0]
    assert "_hash" in result[0]
