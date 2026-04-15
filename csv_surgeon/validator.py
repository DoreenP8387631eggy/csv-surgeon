"""Row validation module for csv-surgeon.

Provides composable validators that check column values against rules
without loading the full dataset into memory.
"""

from typing import Callable, Iterable, Iterator


Row = dict[str, str]
Validator = Callable[[Row], tuple[bool, str]]


def required(column: str) -> Validator:
    """Fail if the column is missing or empty."""
    def _validate(row: Row) -> tuple[bool, str]:
        value = row.get(column, "")
        if value.strip() == "":
            return False, f"Column '{column}' is required but empty"
        return True, ""
    return _validate


def is_numeric(column: str) -> Validator:
    """Fail if the column value cannot be parsed as a float."""
    def _validate(row: Row) -> tuple[bool, str]:
        value = row.get(column, "")
        try:
            float(value)
            return True, ""
        except ValueError:
            return False, f"Column '{column}' value '{value}' is not numeric"
    return _validate


def max_length(column: str, length: int) -> Validator:
    """Fail if the column value exceeds *length* characters."""
    def _validate(row: Row) -> tuple[bool, str]:
        value = row.get(column, "")
        if len(value) > length:
            return False, (
                f"Column '{column}' value exceeds max length {length}"
            )
        return True, ""
    return _validate


def one_of(column: str, choices: list[str]) -> Validator:
    """Fail if the column value is not in *choices*."""
    def _validate(row: Row) -> tuple[bool, str]:
        value = row.get(column, "")
        if value not in choices:
            return False, (
                f"Column '{column}' value '{value}' not in {choices}"
            )
        return True, ""
    return _validate


def validate_rows(
    rows: Iterable[Row],
    validators: list[Validator],
    *,
    fail_fast: bool = False,
) -> Iterator[tuple[Row, list[str]]]:
    """Yield ``(row, errors)`` for every row.

    If *fail_fast* is ``True`` validation stops at the first failing
    validator for each row.
    """
    for row in rows:
        errors: list[str] = []
        for validator in validators:
            ok, message = validator(row)
            if not ok:
                errors.append(message)
                if fail_fast:
                    break
        yield row, errors
