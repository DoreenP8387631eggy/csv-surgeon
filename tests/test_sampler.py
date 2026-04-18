"""Tests for csv_surgeon.sampler."""

import pytest
from csv_surgeon.sampler import (
    sample_first_n,
    sample_random,
    sample_every_nth,
    sample_percentage,
)


@pytest.fixture
def sample_rows():
    return [{"id": str(i), "value": str(i * 10)} for i in range(1, 21)]  # 20 rows


# --- sample_first_n ---

def test_sample_first_n_returns_correct_count(sample_rows):
    result = sample_first_n(iter(sample_rows), 5)
    assert len(result) == 5


def test_sample_first_n_returns_first_rows(sample_rows):
    result = sample_first_n(iter(sample_rows), 3)
    assert result == sample_rows[:3]


def test_sample_first_n_larger_than_stream(sample_rows):
    result = sample_first_n(iter(sample_rows), 100)
    assert len(result) == len(sample_rows)


def test_sample_first_n_zero(sample_rows):
    result = sample_first_n(iter(sample_rows), 0)
    assert result == []


def test_sample_first_n_empty_stream():
    result = sample_first_n(iter([]), 5)
    assert result == []


# --- sample_random ---

def test_sample_random_returns_correct_count(sample_rows):
    result = sample_random(iter(sample_rows), 5, seed=42)
    assert len(result) == 5


def test_sample_random_all_results_from_input(sample_rows):
    result = sample_random(iter(sample_rows), 7, seed=0)
    for row in result:
        assert row in sample_rows


def test_sample_random_reproducible_with_seed(sample_rows):
    r1 = sample_random(iter(sample_rows), 5, seed=99)
    r2 = sample_random(iter(sample_rows), 5, seed=99)
    assert r1 == r2


def test_sample_random_larger_than_stream(sample_rows):
    result = sample_random(iter(sample_rows), 50, seed=1)
    assert len(result) == len(sample_rows)


def test_sample_random_empty_stream():
    result = sample_random(iter([]), 5, seed=42)
    assert result == []


# --- sample_every_nth ---

def test_sample_every_nth_basic(sample_rows):
    result = list(sample_every_nth(iter(sample_rows), 4))
    expected = [sample_rows[i] for i in range(0, 20, 4)]
    assert result == expected


def test_sample_every_nth_with_offset(sample_rows):
    result = list(sample_every_nth(iter(sample_rows), 4, offset=1))
    expected = [sample_rows[i] for i in range(1, 20, 4)]
    assert result == expected


def test_sample_every_nth_invalid_n():
    with pytest.raises(ValueError):
        list(sample_every_nth(iter([]), 0))


def test_sample_every_nth_invalid_offset():
    with pytest.raises(ValueError):
        list(sample_every_nth(iter([]), 3, offset=3))


def test_sample_every_nth_n_of_one(sample_rows):
    """n=1 should return every row."""
    result = list(sample_every_nth(iter(sample_rows), 1))
    assert result == sample_rows


# --- sample_percentage ---

def test_sample_percentage_roughly_correct(sample_rows):
    # With seed and 50%, expect roughly half; exact count varies
    result = list(sample_percentage(iter(sample_rows), 50.0, seed=7))
    assert 3 <= len(result) <= 17  # generous bounds


def test_sample_percentage_100_keeps_all(sample_rows):
    result = list(sample_percentage(iter(sample_rows), 100.0, seed=0))
    assert result == sample_rows


def test_sample_percentage_invalid_zero():
    with pytest.raises(ValueError):
        list(sample_percentage(iter([]), 0.0))


def test_sample_percentage_invalid_over_100():
    with pytest.raises(ValueError):
        list(sample_percentage(iter([]), 101.0))
