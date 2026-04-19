import pytest
from csv_surgeon.encoder import (
    encode_base64, decode_base64,
    encode_url, decode_url,
    encode_html, decode_html,
    encode_hex, decode_hex,
)


@pytest.fixture
def sample_rows():
    return [
        {"id": "1", "value": "hello world"},
        {"id": "2", "value": "foo&bar<baz>"},
        {"id": "3", "value": ""},
    ]


def apply(fn, rows, *args, **kwargs):
    return list(fn(iter(rows), *args, **kwargs))


def test_encode_base64_adds_encoded_value(sample_rows):
    result = apply(encode_base64, sample_rows, "value", "encoded")
    import base64
    assert result[0]["encoded"] == base64.b64encode(b"hello world").decode()


def test_encode_base64_in_place(sample_rows):
    result = apply(encode_base64, sample_rows, "value")
    assert result[0]["value"] != "hello world"


def test_decode_base64_roundtrip(sample_rows):
    encoded = apply(encode_base64, sample_rows, "value", "enc")
    decoded = apply(decode_base64, encoded, "enc", "dec")
    assert decoded[0]["dec"] == "hello world"


def test_decode_base64_invalid_returns_empty():
    rows = [{"value": "not-valid-base64!!!"}]
    result = apply(decode_base64, rows, "value")
    assert result[0]["value"] == ""


def test_encode_url_encodes_spaces(sample_rows):
    result = apply(encode_url, sample_rows, "value", "out")
    assert result[0]["out"] == "hello%20world"


def test_decode_url_roundtrip(sample_rows):
    encoded = apply(encode_url, sample_rows, "value", "enc")
    decoded = apply(decode_url, encoded, "enc", "dec")
    assert decoded[0]["dec"] == "hello world"


def test_encode_html_escapes_ampersand(sample_rows):
    result = apply(encode_html, sample_rows, "value", "out")
    assert "&amp;" in result[1]["out"]


def test_encode_html_escapes_angle_brackets(sample_rows):
    result = apply(encode_html, sample_rows, "value", "out")
    assert "&lt;" in result[1]["out"] and "&gt;" in result[1]["out"]


def test_decode_html_roundtrip(sample_rows):
    encoded = apply(encode_html, sample_rows, "value", "enc")
    decoded = apply(decode_html, encoded, "enc", "dec")
    assert decoded[1]["dec"] == "foo&bar<baz>"


def test_encode_hex_produces_hex_string(sample_rows):
    result = apply(encode_hex, sample_rows, "value", "out")
    assert result[0]["out"] == "hello world".encode().hex()


def test_decode_hex_roundtrip(sample_rows):
    encoded = apply(encode_hex, sample_rows, "value", "enc")
    decoded = apply(decode_hex, encoded, "enc", "dec")
    assert decoded[0]["dec"] == "hello world"


def test_missing_column_is_noop(sample_rows):
    result = apply(encode_base64, sample_rows, "nonexistent", "out")
    assert "out" not in result[0]
    assert result[0]["value"] == "hello world"


def test_empty_value_encodes_without_error(sample_rows):
    result = apply(encode_base64, sample_rows, "value", "out")
    import base64
    assert result[2]["out"] == base64.b64encode(b"").decode()
