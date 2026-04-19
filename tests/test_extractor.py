import pytest
from csv_surgeon.extractor import (
    extract_pattern,
    extract_all_patterns,
    extract_named_groups,
    extract_between,
)


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "text": "Order #12345 placed on 2024-01-15"},
        {"id": "2", "text": "No order here"},
        {"id": "3", "text": "Orders #99 and #100 received"},
    ]


def apply(rows, fn):
    return [fn(r) for r in rows]


def test_extract_pattern_adds_column(sample_rows):
    fn = extract_pattern("text", r"#(\d+)", group=1)
    result = apply(sample_rows, fn)
    assert "text_extracted" in result[0]


def test_extract_pattern_correct_value(sample_rows):
    fn = extract_pattern("text", r"#(\d+)", group=1)
    result = apply(sample_rows, fn)
    assert result[0]["text_extracted"] == "12345"


def test_extract_pattern_no_match_uses_default(sample_rows):
    fn = extract_pattern("text", r"#(\d+)", group=1, default="N/A")
    result = apply(sample_rows, fn)
    assert result[1]["text_extracted"] == "N/A"


def test_extract_pattern_custom_output_col(sample_rows):
    fn = extract_pattern("text", r"\d{4}-\d{2}-\d{2}", output_col="date")
    result = apply(sample_rows, fn)
    assert result[0]["date"] == "2024-01-15"


def test_extract_pattern_preserves_original_fields(sample_rows):
    fn = extract_pattern("text", r"#(\d+)")
    result = apply(sample_rows, fn)
    assert result[0]["id"] == "1"
    assert "text" in result[0]


def test_extract_all_patterns_joins_matches(sample_rows):
    fn = extract_all_patterns("text", r"#(\d+)", group=0)
    result = apply(sample_rows, fn)
    assert result[2]["text_all"] == "#99|#100"


def test_extract_all_patterns_single_match(sample_rows):
    fn = extract_all_patterns("text", r"#\d+")
    result = apply(sample_rows, fn)
    assert result[0]["text_all"] == "#12345"


def test_extract_all_patterns_no_match_default(sample_rows):
    fn = extract_all_patterns("text", r"#\d+", default="none")
    result = apply(sample_rows, fn)
    assert result[1]["text_all"] == "none"


def test_extract_all_patterns_custom_separator(sample_rows):
    fn = extract_all_patterns("text", r"#\d+", separator=",")
    result = apply(sample_rows, fn)
    assert result[2]["text_all"] == "#99,#100"


def test_extract_named_groups_adds_columns():
    rows = [{"val": "John Doe, age 30"}]
    fn = extract_named_groups("val", r"(?P<name>[A-Za-z ]+), age (?P<age>\d+)")
    result = apply(rows, fn)
    assert result[0]["name"] == "John Doe"
    assert result[0]["age"] == "30"


def test_extract_named_groups_no_match_uses_default():
    rows = [{"val": "no match here"}]
    fn = extract_named_groups("val", r"(?P<code>[A-Z]{3}-\d+)", default="-")
    result = apply(rows, fn)
    assert result[0]["code"] == "-"


def test_extract_between_extracts_text():
    rows = [{"val": "Hello [world] bye"}]
    fn = extract_between("val", "[", "]")
    result = apply(rows, fn)
    assert result[0]["val_between"] == "world"


def test_extract_between_no_match_uses_default():
    rows = [{"val": "no brackets"}]
    fn = extract_between("val", "[", "]", default="empty")
    result = apply(rows, fn)
    assert result[0]["val_between"] == "empty"


def test_extract_between_custom_output_col():
    rows = [{"val": "<tag>content</tag>"}]
    fn = extract_between("val", "<tag>", "</tag>", output_col="inner")
    result = apply(rows, fn)
    assert result[0]["inner"] == "content"
