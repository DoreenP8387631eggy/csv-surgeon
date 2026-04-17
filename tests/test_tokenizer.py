import pytest
from csv_surgeon.tokenizer import tokenize_column, token_count_column, filter_by_token


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "tags": "python, data, csv"},
        {"id": "2", "tags": "data|science|ml"},
        {"id": "3", "tags": "python"},
        {"id": "4", "tags": ""},
    ]


def apply(transform, rows):
    return list(transform(iter(rows)))


def test_tokenize_column_adds_output_column(sample_rows):
    result = apply(tokenize_column("tags"), sample_rows)
    assert all("tokens" in r for r in result)


def test_tokenize_column_joins_tokens(sample_rows):
    result = apply(tokenize_column("tags", separator="|"), sample_rows)
    assert result[0]["tokens"] == "python|data|csv"


def test_tokenize_column_custom_output(sample_rows):
    result = apply(tokenize_column("tags", output_column="tag_list"), sample_rows)
    assert "tag_list" in result[0]
    assert "tokens" not in result[0]


def test_tokenize_column_empty_value(sample_rows):
    result = apply(tokenize_column("tags"), sample_rows)
    assert result[3]["tokens"] == ""


def test_tokenize_column_preserves_other_fields(sample_rows):
    result = apply(tokenize_column("tags"), sample_rows)
    assert result[0]["id"] == "1"


def test_token_count_column_correct_count(sample_rows):
    result = apply(token_count_column("tags"), sample_rows)
    assert result[0]["token_count"] == "3"
    assert result[2]["token_count"] == "1"


def test_token_count_column_empty_value(sample_rows):
    result = apply(token_count_column("tags"), sample_rows)
    assert result[3]["token_count"] == "0"


def test_token_count_column_custom_output(sample_rows):
    result = apply(token_count_column("tags", output_column="n_tags"), sample_rows)
    assert "n_tags" in result[0]


def test_token_count_missing_column(sample_rows):
    result = apply(token_count_column("nonexistent"), sample_rows)
    assert all(r["token_count"] == "0" for r in result)


def test_filter_by_token_keeps_matching_rows(sample_rows):
    result = apply(filter_by_token("tags", "python"), sample_rows)
    assert len(result) == 2
    assert all("python" in r["tags"] for r in result)


def test_filter_by_token_case_insensitive(sample_rows):
    rows = [{"id": "1", "tags": "Python, Data"}, {"id": "2", "tags": "csv"}]
    result = apply(filter_by_token("tags", "python", case_sensitive=False), rows)
    assert len(result) == 1


def test_filter_by_token_case_sensitive_no_match(sample_rows):
    result = apply(filter_by_token("tags", "Python", case_sensitive=True), sample_rows)
    assert len(result) == 0


def test_filter_by_token_no_match_returns_empty(sample_rows):
    result = apply(filter_by_token("tags", "java"), sample_rows)
    assert result == []
