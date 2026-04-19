import pytest
from csv_surgeon.splitter_regex import split_on_pattern, split_on_delimiter, split_keep_original


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "tags": "alpha,beta,gamma"},
        {"id": "2", "tags": "delta"},
        {"id": "3", "tags": ""},
    ]


def test_split_on_delimiter_expands_multiple(sample_rows):
    result = list(split_on_delimiter(iter(sample_rows), column="tags"))
    assert len(result) == 5  # 3 + 1 (delta unchanged) + 1 (empty unchanged)


def test_split_on_delimiter_correct_values(sample_rows):
    result = list(split_on_delimiter(iter(sample_rows), column="tags"))
    tags = [r["tags"] for r in result]
    assert "alpha" in tags
    assert "beta" in tags
    assert "gamma" in tags


def test_split_on_delimiter_single_value_unchanged(sample_rows):
    result = list(split_on_delimiter(iter(sample_rows), column="tags"))
    delta_rows = [r for r in result if r["tags"] == "delta"]
    assert len(delta_rows) == 1


def test_split_on_delimiter_output_column():
    rows = [{"id": "1", "raw": "a,b,c"}]
    result = list(split_on_delimiter(iter(rows), column="raw", output_column="item"))
    assert len(result) == 3
    assert all("raw" in r for r in result)
    assert result[0]["item"] == "a"


def test_split_on_delimiter_strips_whitespace():
    rows = [{"id": "1", "tags": "a , b , c"}]
    result = list(split_on_delimiter(iter(rows), column="tags", strip=True))
    assert result[0]["tags"] == "a"
    assert result[1]["tags"] == "b"


def test_split_on_delimiter_no_strip():
    rows = [{"id": "1", "tags": "a , b"}]
    result = list(split_on_delimiter(iter(rows), column="tags", strip=False))
    assert result[0]["tags"] == "a "


def test_split_on_pattern_extracts_matches():
    rows = [{"id": "1", "text": "foo123bar456"}]
    result = list(split_on_pattern(iter(rows), column="text", pattern=r"\d+"))
    assert len(result) == 2
    assert result[0]["text"] == "123"
    assert result[1]["text"] == "456"


def test_split_on_pattern_no_match_passes_through():
    rows = [{"id": "1", "text": "no digits here"}]
    result = list(split_on_pattern(iter(rows), column="text", pattern=r"\d+"))
    assert len(result) == 1
    assert result[0]["text"] == "no digits here"


def test_split_on_pattern_output_column():
    rows = [{"id": "1", "text": "abc123"}]
    result = list(split_on_pattern(iter(rows), column="text", pattern=r"\d+", output_column="num"))
    assert result[0]["num"] == "123"
    assert result[0]["text"] == "abc123"


def test_split_keep_original_no_match_yields_empty_output():
    rows = [{"id": "1", "text": "hello"}]
    result = list(split_keep_original(iter(rows), column="text", pattern=r"\d+", output_column="num"))
    assert len(result) == 1
    assert result[0]["num"] == ""
    assert result[0]["text"] == "hello"


def test_split_keep_original_preserves_original_column():
    rows = [{"id": "1", "text": "abc123def456"}]
    result = list(split_keep_original(iter(rows), column="text", pattern=r"\d+", output_column="num"))
    assert all(r["text"] == "abc123def456" for r in result)
    assert len(result) == 2
