"""Tests for csv_surgeon.hasher."""

import hashlib
import pytest

from csv_surgeon.hasher import hash_column, hash_row, truncate_hash


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "dept": "eng", "salary": "90000"},
        {"name": "Bob", "dept": "hr", "salary": "60000"},
        {"name": "", "dept": "eng", "salary": "70000"},
    ]


def apply(transform, rows):
    return [transform(r) for r in rows]


# ---------------------------------------------------------------------------
# hash_column
# ---------------------------------------------------------------------------

def test_hash_column_adds_output_column(sample_rows):
    result = apply(hash_column("name"), sample_rows)
    assert "name_hash" in result[0]


def test_hash_column_correct_sha256(sample_rows):
    result = apply(hash_column("name"), sample_rows)
    expected = hashlib.sha256(b"Alice").hexdigest()
    assert result[0]["name_hash"] == expected


def test_hash_column_custom_output_col(sample_rows):
    result = apply(hash_column("name", output_col="hashed_name"), sample_rows)
    assert "hashed_name" in result[0]
    assert "name_hash" not in result[0]


def test_hash_column_md5_algorithm(sample_rows):
    result = apply(hash_column("name", algorithm="md5"), sample_rows)
    expected = hashlib.md5(b"Alice").hexdigest()
    assert result[0]["name_hash"] == expected


def test_hash_column_empty_value(sample_rows):
    result = apply(hash_column("name"), sample_rows)
    expected = hashlib.sha256(b"").hexdigest()
    assert result[2]["name_hash"] == expected


def test_hash_column_missing_column_uses_empty(sample_rows):
    result = apply(hash_column("nonexistent"), sample_rows)
    expected = hashlib.sha256(b"").hexdigest()
    assert result[0]["nonexistent_hash"] == expected


def test_hash_column_preserves_original_fields(sample_rows):
    result = apply(hash_column("name"), sample_rows)
    assert result[0]["name"] == "Alice"
    assert result[0]["dept"] == "eng"


def test_hash_column_hmac_differs_from_plain(sample_rows):
    plain = apply(hash_column("name"), sample_rows)
    hmac_result = apply(hash_column("name", secret="mysecret"), sample_rows)
    assert plain[0]["name_hash"] != hmac_result[0]["name_hash"]


def test_hash_column_hmac_deterministic(sample_rows):
    r1 = apply(hash_column("name", secret="key"), sample_rows)
    r2 = apply(hash_column("name", secret="key"), sample_rows)
    assert r1[0]["name_hash"] == r2[0]["name_hash"]


# ---------------------------------------------------------------------------
# hash_row
# ---------------------------------------------------------------------------

def test_hash_row_adds_default_column(sample_rows):
    result = apply(hash_row(), sample_rows)
    assert "row_hash" in result[0]


def test_hash_row_custom_output_col(sample_rows):
    result = apply(hash_row(output_col="sig"), sample_rows)
    assert "sig" in result[0]


def test_hash_row_different_rows_have_different_hashes(sample_rows):
    result = apply(hash_row(), sample_rows)
    assert result[0]["row_hash"] != result[1]["row_hash"]


def test_hash_row_subset_of_columns(sample_rows):
    full = apply(hash_row(), sample_rows)
    subset = apply(hash_row(columns=["name"]), sample_rows)
    assert full[0]["row_hash"] != subset[0]["row_hash"]


def test_hash_row_preserves_original_fields(sample_rows):
    result = apply(hash_row(), sample_rows)
    assert result[0]["name"] == "Alice"


# ---------------------------------------------------------------------------
# truncate_hash
# ---------------------------------------------------------------------------

def test_truncate_hash_shortens_value():
    row = {"name_hash": "abcdef1234567890"}
    result = truncate_hash("name_hash", length=8)(row)
    assert result["name_hash_short"] == "abcdef12"


def test_truncate_hash_custom_output_col():
    row = {"name_hash": "abcdef1234567890"}
    result = truncate_hash("name_hash", length=4, output_col="short")(row)
    assert result["short"] == "abcd"


def test_truncate_hash_preserves_original_column():
    row = {"name_hash": "abcdef1234567890"}
    result = truncate_hash("name_hash", length=4)(row)
    assert result["name_hash"] == "abcdef1234567890"
