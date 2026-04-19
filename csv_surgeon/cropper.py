"""Column value cropping: remove leading/trailing characters or substrings."""
from typing import Iterable, Iterator


def _transform(rows, col, fn):
    for row in rows:
        out = dict(row)
        if col in out:
            out[col] = fn(out[col])
        yield out


def lstrip_column(rows: Iterable[dict], col: str, chars: str = None) -> Iterator[dict]:
    """Strip leading characters from a column."""
    return _transform(rows, col, lambda v: v.lstrip(chars))


def rstrip_column(rows: Iterable[dict], col: str, chars: str = None) -> Iterator[dict]:
    """Strip trailing characters from a column."""
    return _transform(rows, col, lambda v: v.rstrip(chars))


def strip_column(rows: Iterable[dict], col: str, chars: str = None) -> Iterator[dict]:
    """Strip leading and trailing characters from a column."""
    return _transform(rows, col, lambda v: v.strip(chars))


def remove_prefix(rows: Iterable[dict], col: str, prefix: str) -> Iterator[dict]:
    """Remove a fixed prefix from a column value if present."""
    def _fn(v):
        return v[len(prefix):] if v.startswith(prefix) else v
    return _transform(rows, col, _fn)


def remove_suffix(rows: Iterable[dict], col: str, suffix: str) -> Iterator[dict]:
    """Remove a fixed suffix from a column value if present."""
    def _fn(v):
        return v[:-len(suffix)] if suffix and v.endswith(suffix) else v
    return _transform(rows, col, _fn)
