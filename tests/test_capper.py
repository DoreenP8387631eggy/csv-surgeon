import pytest
from csv_surgeon.capper import cap_words, cap_chars, cap_sentences


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "text": "the quick brown fox jumps", "note": "hello world"},
        {"id": "2", "text": "one two three", "note": ""},
        {"id": "3", "text": "single", "note": "a b c d e"},
    ]


def apply(fn, rows, *args, **kwargs):
    return list(fn(iter(rows), *args, **kwargs))


# --- cap_words ---

def test_cap_words_limits_to_max(sample_rows):
    result = apply(cap_words, sample_rows, "text", 3)
    assert result[0]["text"] == "the quick brown"


def test_cap_words_short_value_unchanged(sample_rows):
    result = apply(cap_words, sample_rows, "text", 10)
    assert result[1]["text"] == "one two three"


def test_cap_words_single_word(sample_rows):
    result = apply(cap_words, sample_rows, "text", 1)
    assert result[2]["text"] == "single"


def test_cap_words_out_col_preserves_original(sample_rows):
    result = apply(cap_words, sample_rows, "text", 2, out_col="short")
    assert result[0]["text"] == "the quick brown fox jumps"
    assert result[0]["short"] == "the quick"


def test_cap_words_missing_column_is_noop(sample_rows):
    result = apply(cap_words, sample_rows, "missing", 2)
    assert result[0] == sample_rows[0]


def test_cap_words_empty_value(sample_rows):
    result = apply(cap_words, sample_rows, "note", 3)
    assert result[1]["note"] == ""


# --- cap_chars ---

def test_cap_chars_truncates_long_value(sample_rows):
    result = apply(cap_chars, sample_rows, "text", 9)
    assert result[0]["text"] == "the quick"


def test_cap_chars_short_value_unchanged(sample_rows):
    result = apply(cap_chars, sample_rows, "text", 100)
    assert result[2]["text"] == "single"


def test_cap_chars_ellipsis_appended(sample_rows):
    result = apply(cap_chars, sample_rows, "text", 12, ellipsis="...")
    assert result[0]["text"].endswith("...")
    assert len(result[0]["text"]) == 12


def test_cap_chars_out_col(sample_rows):
    result = apply(cap_chars, sample_rows, "text", 3, out_col="tiny")
    assert result[0]["tiny"] == "the"
    assert "text" in result[0]


def test_cap_chars_missing_column_is_noop(sample_rows):
    result = apply(cap_chars, sample_rows, "nope", 5)
    assert result[0] == sample_rows[0]


# --- cap_sentences ---

def test_cap_sentences_limits_sentences():
    rows = [{"text": "Hello world. How are you? Fine thanks."}]
    result = apply(cap_sentences, rows, "text", 2)
    assert result[0]["text"] == "Hello world. How are you?"


def test_cap_sentences_single_sentence_unchanged():
    rows = [{"text": "Just one sentence."}]
    result = apply(cap_sentences, rows, "text", 3)
    assert result[0]["text"] == "Just one sentence."


def test_cap_sentences_out_col():
    rows = [{"text": "One. Two. Three."}]
    result = apply(cap_sentences, rows, "text", 1, out_col="first")
    assert result[0]["first"] == "One."
    assert result[0]["text"] == "One. Two. Three."
