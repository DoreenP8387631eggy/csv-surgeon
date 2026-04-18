import pytest
from csv_surgeon.zipper import zip_columns, unzip_column, zip_with


@pytest.fixture
def sample_rows():
    return [
        {"first": "John", "last": "Doe", "age": "30"},
        {"first": "Jane", "last": "Smith", "age": "25"},
        {"first": "", "last": "Brown", "age": "40"},
    ]


def test_zip_columns_combines_values(sample_rows):
    result = list(zip_columns(iter(sample_rows), "first", "last", "full_name"))
    assert result[0]["full_name"] == "John|Doe"
    assert result[1]["full_name"] == "Jane|Smith"


def test_zip_columns_custom_separator(sample_rows):
    result = list(zip_columns(iter(sample_rows), "first", "last", "full_name", separator=" "))
    assert result[0]["full_name"] == "John Doe"


def test_zip_columns_preserves_original_by_default(sample_rows):
    result = list(zip_columns(iter(sample_rows), "first", "last", "full_name"))
    assert "first" in result[0]
    assert "last" in result[0]


def test_zip_columns_drop_originals(sample_rows):
    result = list(zip_columns(iter(sample_rows), "first", "last", "full_name", drop_originals=True))
    assert "first" not in result[0]
    assert "last" not in result[0]
    assert "full_name" in result[0]


def test_zip_columns_empty_value(sample_rows):
    result = list(zip_columns(iter(sample_rows), "first", "last", "full_name"))
    assert result[2]["full_name"] == "|Brown"


def test_unzip_column_splits_value():
    rows = [{"full_name": "John|Doe", "age": "30"}]
    result = list(unzip_column(iter(rows), "full_name", ["first", "last"]))
    assert result[0]["first"] == "John"
    assert result[0]["last"] == "Doe"


def test_unzip_column_custom_separator():
    rows = [{"full_name": "John Doe"}]
    result = list(unzip_column(iter(rows), "full_name", ["first", "last"], separator=" "))
    assert result[0]["first"] == "John"
    assert result[0]["last"] == "Doe"


def test_unzip_column_pads_missing_parts():
    rows = [{"full_name": "OnlyOne"}]
    result = list(unzip_column(iter(rows), "full_name", ["a", "b", "c"]))
    assert result[0]["a"] == "OnlyOne"
    assert result[0]["b"] == ""
    assert result[0]["c"] == ""


def test_unzip_column_drop_original():
    rows = [{"full_name": "John|Doe"}]
    result = list(unzip_column(iter(rows), "full_name", ["first", "last"], drop_original=True))
    assert "full_name" not in result[0]


def test_zip_with_custom_fn(sample_rows):
    fn = lambda a, b: f"{a.upper()} {b.lower()}"
    result = list(zip_with(iter(sample_rows), "first", "last", "combined", fn))
    assert result[0]["combined"] == "JOHN doe"


def test_zip_with_drop_originals(sample_rows):
    fn = lambda a, b: a + b
    result = list(zip_with(iter(sample_rows), "first", "last", "combined", fn, drop_originals=True))
    assert "first" not in result[0]
    assert "last" not in result[0]
