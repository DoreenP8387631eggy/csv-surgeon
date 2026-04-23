"""Column hashing utilities for csv-surgeon."""

import hashlib
import hmac
from typing import Iterator, Optional


def _hash_value(value: str, algorithm: str, secret: Optional[str] = None) -> str:
    """Hash a single string value using the given algorithm."""
    encoded = value.encode("utf-8")
    if secret:
        key = secret.encode("utf-8")
        h = hmac.new(key, encoded, algorithm)
        return h.hexdigest()
    h = hashlib.new(algorithm)
    h.update(encoded)
    return h.hexdigest()


def hash_column(
    column: str,
    algorithm: str = "sha256",
    output_col: Optional[str] = None,
    secret: Optional[str] = None,
):
    """Return a transform that hashes *column* and writes the digest.

    Args:
        column:     Source column to hash.
        algorithm:  Any algorithm supported by :mod:`hashlib` (e.g. ``md5``,
                    ``sha1``, ``sha256``, ``sha512``).
        output_col: Destination column name.  Defaults to ``<column>_hash``.
        secret:     Optional HMAC secret.  When provided the digest is computed
                    with :func:`hmac.new` instead of plain :mod:`hashlib`.
    """
    out = output_col or f"{column}_hash"

    def _transform(row: dict) -> dict:
        value = row.get(column, "")
        result = dict(row)
        result[out] = _hash_value(value, algorithm, secret)
        return result

    return _transform


def hash_row(
    columns: Optional[list] = None,
    algorithm: str = "sha256",
    output_col: str = "row_hash",
    separator: str = "|",
):
    """Return a transform that hashes a composite key built from *columns*.

    Args:
        columns:    Ordered list of columns to include.  ``None`` means all
                    columns in insertion order.
        algorithm:  Hashing algorithm (see :func:`hash_column`).
        output_col: Destination column for the digest.
        separator:  String used to join column values before hashing.
    """

    def _transform(row: dict) -> dict:
        keys = columns if columns is not None else list(row.keys())
        composite = separator.join(row.get(k, "") for k in keys)
        result = dict(row)
        result[output_col] = _hash_value(composite, algorithm)
        return result

    return _transform


def truncate_hash(
    column: str,
    length: int = 8,
    output_col: Optional[str] = None,
):
    """Return a transform that shortens an existing hash column to *length* chars."""
    out = output_col or f"{column}_short"

    def _transform(row: dict) -> dict:
        result = dict(row)
        result[out] = row.get(column, "")[:length]
        return result

    return _transform
