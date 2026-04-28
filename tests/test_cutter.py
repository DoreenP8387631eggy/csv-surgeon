"""Tests for csv_surgeon/cutter.py."""
import pytest
from csv_surgeon.cutter import cut_chars, cut_before, cut_after, cut_words


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "text": "hello world", "extra": "a"},
        {"id": "2", "text": "foo:bar:baz", "extra": "b"},
        {"id": "3", "text": "one two three", "extra": "c"},
    ]


def apply(fn, rows):
    return list(fn(rows))


# --- cut_chars ---

def test_cut_chars_basic(sample_rows):
    result = apply(lambda r: cut_chars(r, "text", 0, 5), sample_rows)
    assert result[0]["text"] == "hello"


def test_cut_chars_mid_range(sample_rows):
    result = apply(lambda r: cut_chars(r, "text", 6, 11), sample_rows)
    assert result[0]["text"] == "world"


def test_cut_chars_no_end(sample_rows):
    result = apply(lambda r: cut_chars(r, "text", 4), sample_rows)
    assert result[0]["text"] == "o world"


def test_cut_chars_out_col(sample_rows):
    result = apply(lambda r: cut_chars(r, "text", 0, 3, out_col="short"), sample_rows)
    assert result[0]["short"] == "hel"
    assert result[0]["text"] == "hello world"  # original unchanged


def test_cut_chars_missing_column(sample_rows):
    result = apply(lambda r: cut_chars(r, "missing", 0, 3), sample_rows)
    assert result[0] == sample_rows[0]  # row unchanged


def test_cut_chars_preserves_other_columns(sample_rows):
    result = apply(lambda r: cut_chars(r, "text", 0, 5), sample_rows)
    assert result[0]["id"] == "1"
    assert result[0]["extra"] == "a"


# --- cut_before ---

def test_cut_before_finds_separator(sample_rows):
    result = apply(lambda r: cut_before(r, "text", ":"), sample_rows)
    assert result[1]["text"] == "foo"


def test_cut_before_no_separator_returns_full(sample_rows):
    result = apply(lambda r: cut_before(r, "text", ":"), sample_rows)
    assert result[0]["text"] == "hello world"  # no colon


def test_cut_before_out_col(sample_rows):
    result = apply(lambda r: cut_before(r, "text", ":", out_col="prefix"), sample_rows)
    assert result[1]["prefix"] == "foo"
    assert result[1]["text"] == "foo:bar:baz"


# --- cut_after ---

def test_cut_after_finds_separator(sample_rows):
    result = apply(lambda r: cut_after(r, "text", ":"), sample_rows)
    assert result[1]["text"] == "bar:baz"


def test_cut_after_no_separator_returns_full(sample_rows):
    result = apply(lambda r: cut_after(r, "text", ":"), sample_rows)
    assert result[0]["text"] == "hello world"


def test_cut_after_out_col(sample_rows):
    result = apply(lambda r: cut_after(r, "text", ":", out_col="suffix"), sample_rows)
    assert result[1]["suffix"] == "bar:baz"
    assert result[1]["text"] == "foo:bar:baz"


# --- cut_words ---

def test_cut_words_first_word(sample_rows):
    result = apply(lambda r: cut_words(r, "text", 0, 1), sample_rows)
    assert result[2]["text"] == "one"


def test_cut_words_last_two(sample_rows):
    result = apply(lambda r: cut_words(r, "text", 1), sample_rows)
    assert result[2]["text"] == "two three"


def test_cut_words_out_col(sample_rows):
    result = apply(lambda r: cut_words(r, "text", 0, 1, out_col="first_word"), sample_rows)
    assert result[0]["first_word"] == "hello"
    assert result[0]["text"] == "hello world"


def test_cut_words_preserves_row_count(sample_rows):
    result = apply(lambda r: cut_words(r, "text", 0, 1), sample_rows)
    assert len(result) == len(sample_rows)
