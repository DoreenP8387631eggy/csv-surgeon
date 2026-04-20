"""Tests for csv_surgeon.stemmer."""
import pytest
from csv_surgeon.stemmer import stem_column, unique_stems, _simple_stem


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "text": "running quickly"},
        {"id": "2", "text": "happiness and sadness"},
        {"id": "3", "text": "jumped over"},
        {"id": "4", "text": ""},
    ]


# --- _simple_stem ---

def test_simple_stem_removes_ing():
    assert _simple_stem("running") == "runn"


def test_simple_stem_removes_ly():
    assert _simple_stem("quickly") == "quick"


def test_simple_stem_removes_ness():
    assert _simple_stem("happiness") == "happi"


def test_simple_stem_short_word_unchanged():
    assert _simple_stem("run") == "run"


def test_simple_stem_lowercases():
    assert _simple_stem("JUMPING") == "jump"


# --- stem_column ---

def test_stem_column_adds_out_col(sample_rows):
    result = list(stem_column(iter(sample_rows), "text", out_col="stemmed"))
    assert "stemmed" in result[0]


def test_stem_column_in_place(sample_rows):
    result = list(stem_column(iter(sample_rows), "text"))
    assert result[0]["text"] != "running quickly"


def test_stem_column_preserves_other_fields(sample_rows):
    result = list(stem_column(iter(sample_rows), "text", out_col="stemmed"))
    assert result[1]["id"] == "2"


def test_stem_column_empty_value_unchanged(sample_rows):
    result = list(stem_column(iter(sample_rows), "text"))
    assert result[3]["text"] == ""


def test_stem_column_missing_column_is_noop():
    rows = [{"a": "hello"}]
    result = list(stem_column(iter(rows), "missing"))
    assert result[0] == {"a": "hello"}


def test_stem_column_custom_stemmer(sample_rows):
    result = list(stem_column(iter(sample_rows), "text", out_col="s", stemmer=lambda w: w[:3]))
    assert result[0]["s"] == "run qui"


# --- unique_stems ---

def test_unique_stems_adds_column(sample_rows):
    result = list(unique_stems(iter(sample_rows), "text"))
    assert "stems" in result[0]


def test_unique_stems_no_duplicates():
    rows = [{"text": "test testing tested test"}]
    result = list(unique_stems(iter(rows), "text"))
    stems = result[0]["stems"].split()
    assert len(stems) == len(set(stems))


def test_unique_stems_custom_out_col(sample_rows):
    result = list(unique_stems(iter(sample_rows), "text", out_col="roots"))
    assert "roots" in result[0]


def test_unique_stems_custom_separator(sample_rows):
    result = list(unique_stems(iter(sample_rows), "text", separator=","))
    assert "," in result[0]["stems"]


def test_unique_stems_missing_column_is_noop():
    rows = [{"a": "x"}]
    result = list(unique_stems(iter(rows), "missing"))
    assert result[0] == {"a": "x"}
