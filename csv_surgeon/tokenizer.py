"""Tokenizer: split column values into tokens and expand or count them."""
from typing import Iterator, Dict, Any, Callable, List
import re


def _default_split(value: str) -> List[str]:
    return re.split(r'[\s,;|]+', value.strip())


def tokenize_column(
    column: str,
    output_column: str = "tokens",
    splitter: Callable[[str], List[str]] = _default_split,
    separator: str = "|",
) -> Callable[[Iterator[Dict[str, Any]]], Iterator[Dict[str, Any]]]:
    """Add a column containing joined tokens derived from splitting *column*."""
    def _transform(rows: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for row in rows:
            new = dict(row)
            value = row.get(column, "")
            tokens = [t for t in splitter(value) if t]
            new[output_column] = separator.join(tokens)
            yield new
    return _transform


def token_count_column(
    column: str,
    output_column: str = "token_count",
    splitter: Callable[[str], List[str]] = _default_split,
) -> Callable[[Iterator[Dict[str, Any]]], Iterator[Dict[str, Any]]]:
    """Add a column with the number of tokens in *column*."""
    def _transform(rows: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for row in rows:
            new = dict(row)
            value = row.get(column, "")
            tokens = [t for t in splitter(value) if t]
            new[output_column] = str(len(tokens))
            yield new
    return _transform


def filter_by_token(
    column: str,
    token: str,
    splitter: Callable[[str], List[str]] = _default_split,
    case_sensitive: bool = False,
) -> Callable[[Iterator[Dict[str, Any]]], Iterator[Dict[str, Any]]]:
    """Keep only rows where *column* contains *token* after splitting."""
    needle = token if case_sensitive else token.lower()

    def _transform(rows: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for row in rows:
            value = row.get(column, "")
            tokens = [t for t in splitter(value) if t]
            haystack = tokens if case_sensitive else [t.lower() for t in tokens]
            if needle in haystack:
                yield row
    return _transform
