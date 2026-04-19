"""Column encoding utilities: base64, url, html, and hex encoding/decoding."""
import base64
import urllib.parse
import html
from typing import Iterator, Dict


def _transform(rows, col, fn, out_col):
    for row in rows:
        new = dict(row)
        if col in new:
            new[out_col] = fn(new[col])
        yield new


def encode_base64(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    def _enc(v):
        try:
            return base64.b64encode(v.encode()).decode()
        except Exception:
            return ""
    return _transform(rows, column, _enc, out)


def decode_base64(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    def _dec(v):
        try:
            return base64.b64decode(v.encode()).decode()
        except Exception:
            return ""
    return _transform(rows, column, _dec, out)


def encode_url(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    return _transform(rows, column, urllib.parse.quote, out)


def decode_url(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    return _transform(rows, column, urllib.parse.unquote, out)


def encode_html(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    return _transform(rows, column, html.escape, out)


def decode_html(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    return _transform(rows, column, html.unescape, out)


def encode_hex(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    def _enc(v):
        try:
            return v.encode().hex()
        except Exception:
            return ""
    return _transform(rows, column, _enc, out)


def decode_hex(rows: Iterator[Dict], column: str, output_column: str = None) -> Iterator[Dict]:
    out = output_column or column
    def _dec(v):
        try:
            return bytes.fromhex(v).decode()
        except Exception:
            return ""
    return _transform(rows, column, _dec, out)
