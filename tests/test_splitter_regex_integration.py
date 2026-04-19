"""Integration tests: chain splitter_regex with filters and transforms."""
from csv_surgeon.splitter_regex import split_on_delimiter, split_on_pattern
from csv_surgeon.filters import contains
from csv_surgeon.pipeline import FilterPipeline


def _make_rows():
    return [
        {"id": "1", "categories": "sports,news,tech", "score": "10"},
        {"id": "2", "categories": "arts", "score": "5"},
        {"id": "3", "categories": "news,finance", "score": "8"},
    ]


def test_split_then_count_total_rows():
    rows = list(split_on_delimiter(iter(_make_rows()), column="categories"))
    assert len(rows) == 6  # 3+1+2


def test_split_then_filter_by_category():
    rows = split_on_delimiter(iter(_make_rows()), column="categories")
    pipeline = FilterPipeline()
    pipeline.add_filter(contains("categories", "news"))
    result = list(pipeline.run(rows))
    assert len(result) == 2
    assert all(r["categories"] == "news" for r in result)


def test_split_preserves_other_columns():
    rows = list(split_on_delimiter(iter(_make_rows()), column="categories"))
    assert all("id" in r and "score" in r for r in rows)


def test_split_pattern_then_collect():
    data = [
        {"id": "1", "refs": "ref:001 ref:002"},
        {"id": "2", "refs": "ref:003"},
    ]
    rows = list(split_on_pattern(iter(data), column="refs", pattern=r"ref:\d+"))
    assert len(rows) == 3
    assert rows[0]["refs"] == "ref:001"
    assert rows[2]["refs"] == "ref:003"


def test_split_output_column_does_not_lose_rows():
    data = [{"id": str(i), "vals": "a,b,c"} for i in range(5)]
    rows = list(split_on_delimiter(iter(data), column="vals", output_column="val"))
    assert len(rows) == 15
    assert all(r["vals"] == "a,b,c" for r in rows)
