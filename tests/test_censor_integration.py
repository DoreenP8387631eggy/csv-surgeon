"""Integration tests for the censor pipeline."""
from csv_surgeon.censor import censor_column, censor_pattern, censor_columns
from csv_surgeon.filters import contains
from csv_surgeon.pipeline import FilterPipeline


def _make_rows():
    return [
        {"name": "Alice", "email": "alice@example.com", "dept": "eng"},
        {"name": "Bob", "email": "bob@other.org", "dept": "hr"},
        {"name": "Carol", "email": "carol@example.com", "dept": "eng"},
    ]


def test_censor_then_filter_preserves_row_count():
    rows = censor_column(_make_rows(), "email")
    result = list(rows)
    assert len(result) == 3


def test_censor_then_filter_by_dept():
    rows = censor_column(_make_rows(), "email")
    pipeline = FilterPipeline()
    pipeline.add_filter(contains("dept", "eng"))
    result = list(pipeline.run(rows))
    assert len(result) == 2
    assert all(r["email"] == "***" for r in result)


def test_censor_pattern_then_censor_column_chain():
    rows = censor_pattern(_make_rows(), "email", r"@.*", replacement="@[HIDDEN]")
    rows = censor_column(rows, "name")
    result = list(rows)
    assert result[0]["name"] == "***"
    assert result[0]["email"] == "alice@[HIDDEN]"


def test_censor_columns_preserves_all_rows():
    rows = censor_columns(_make_rows(), ["name", "email"])
    result = list(rows)
    assert len(result) == 3


def test_censor_does_not_affect_uncensored_column():
    rows = censor_columns(_make_rows(), ["name", "email"])
    result = list(rows)
    depts = {r["dept"] for r in result}
    assert depts == {"eng", "hr"}
