import pytest
from csv_surgeon.linker import link_column, link_exists, link_count


@pytest.fixture
def left_rows():
    return [
        {"id": "1", "name": "Alice"},
        {"id": "2", "name": "Bob"},
        {"id": "3", "name": "Carol"},
    ]


@pytest.fixture
def right_rows():
    return [
        {"user_id": "1", "tag": "admin"},
        {"user_id": "1", "tag": "editor"},
        {"user_id": "2", "tag": "viewer"},
    ]


def test_link_column_joins_values(left_rows, right_rows):
    result = list(link_column(iter(left_rows), iter(right_rows), "id", "user_id", "tags", "tag"))
    assert result[0]["tags"] == "admin|editor"


def test_link_column_single_match(left_rows, right_rows):
    result = list(link_column(iter(left_rows), iter(right_rows), "id", "user_id", "tags", "tag"))
    assert result[1]["tags"] == "viewer"


def test_link_column_no_match_uses_default(left_rows, right_rows):
    result = list(link_column(iter(left_rows), iter(right_rows), "id", "user_id", "tags", "tag", default="none"))
    assert result[2]["tags"] == "none"


def test_link_column_preserves_original_fields(left_rows, right_rows):
    result = list(link_column(iter(left_rows), iter(right_rows), "id", "user_id", "tags", "tag"))
    assert result[0]["name"] == "Alice"


def test_link_column_custom_separator(left_rows, right_rows):
    result = list(link_column(iter(left_rows), iter(right_rows), "id", "user_id", "tags", "tag", separator=","))
    assert result[0]["tags"] == "admin,editor"


def test_link_exists_true_when_match(left_rows, right_rows):
    result = list(link_exists(iter(left_rows), iter(right_rows), "id", "user_id"))
    assert result[0]["linked"] == "true"
    assert result[1]["linked"] == "true"


def test_link_exists_false_when_no_match(left_rows, right_rows):
    result = list(link_exists(iter(left_rows), iter(right_rows), "id", "user_id"))
    assert result[2]["linked"] == "false"


def test_link_exists_custom_values(left_rows, right_rows):
    result = list(link_exists(iter(left_rows), iter(right_rows), "id", "user_id", true_value="yes", false_value="no"))
    assert result[0]["linked"] == "yes"
    assert result[2]["linked"] == "no"


def test_link_exists_custom_output_col(left_rows, right_rows):
    result = list(link_exists(iter(left_rows), iter(right_rows), "id", "user_id", output_col="has_tag"))
    assert "has_tag" in result[0]


def test_link_count_correct_value(left_rows, right_rows):
    result = list(link_count(iter(left_rows), iter(right_rows), "id", "user_id"))
    assert result[0]["link_count"] == "2"
    assert result[1]["link_count"] == "1"
    assert result[2]["link_count"] == "0"


def test_link_count_custom_output_col(left_rows, right_rows):
    result = list(link_count(iter(left_rows), iter(right_rows), "id", "user_id", output_col="n_tags"))
    assert "n_tags" in result[0]


def test_link_count_preserves_fields(left_rows, right_rows):
    result = list(link_count(iter(left_rows), iter(right_rows), "id", "user_id"))
    assert result[0]["name"] == "Alice"
