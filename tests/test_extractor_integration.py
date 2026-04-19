import pytest
from csv_surgeon.extractor import extract_pattern, extract_all_patterns, extract_between, extract_named_groups
from csv_surgeon.filters import contains
from csv_surgeon.pipeline import FilterPipeline


def _make_rows():
    return [
        {"id": "1", "log": "ERROR [auth] token=abc123 user=alice"},
        {"id": "2", "log": "INFO [db] query completed in 42ms"},
        {"id": "3", "log": "ERROR [api] token=xyz789 user=bob"},
        {"id": "4", "log": "DEBUG nothing special"},
    ]


def test_extract_then_filter_by_extracted_value():
    rows = _make_rows()
    extract = extract_pattern("log", r"token=(\w+)", output_col="token", group=1)
    extracted = [extract(r) for r in rows]
    pipeline = FilterPipeline()
    pipeline.add_filter(contains("log", "ERROR"))
    result = [r for r in extracted if pipeline._row_passes(r)]
    assert len(result) == 2
    assert all(r["token"] != "" for r in result)


def test_extract_preserves_all_rows():
    rows = _make_rows()
    fn = extract_pattern("log", r"\d+ms", output_col="duration")
    result = [fn(r) for r in rows]
    assert len(result) == len(rows)


def test_extract_preserves_all_columns():
    rows = _make_rows()
    fn = extract_pattern("log", r"ERROR", output_col="error_flag")
    result = [fn(r) for r in rows]
    assert all("id" in r and "log" in r and "error_flag" in r for r in result)


def test_chain_multiple_extractions():
    rows = _make_rows()
    e1 = extract_pattern("log", r"token=(\w+)", output_col="token", group=1)
    e2 = extract_pattern("log", r"user=(\w+)", output_col="user", group=1)
    result = [e2(e1(r)) for r in rows]
    assert result[0]["token"] == "abc123"
    assert result[0]["user"] == "alice"
    assert result[1]["token"] == ""
    assert result[1]["user"] == ""


def test_extract_all_then_count_tokens():
    rows = [{"id": str(i), "tags": f"#a #b #c"} for i in range(5)]
    fn = extract_all_patterns("tags", r"#\w+", output_col="all_tags", separator=",")
    result = [fn(r) for r in rows]
    assert all(r["all_tags"] == "#a,#b,#c" for r in result)
