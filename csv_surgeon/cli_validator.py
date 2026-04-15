"""CLI sub-command for validating CSV files."""

import csv
import sys
from argparse import ArgumentParser, Namespace

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.validator import (
    required,
    is_numeric,
    max_length,
    one_of,
    validate_rows,
)


def _build_validators(args: Namespace) -> list:
    validators = []

    for col in args.required or []:
        validators.append(required(col))

    for col in args.numeric or []:
        validators.append(is_numeric(col))

    for spec in args.max_length or []:
        # format: "column:length"
        col, length_str = spec.split(":", 1)
        validators.append(max_length(col, int(length_str)))

    for spec in args.one_of or []:
        # format: "column:val1,val2,..."
        col, values_str = spec.split(":", 1)
        choices = values_str.split(",")
        validators.append(one_of(col, choices))

    return validators


def cmd_validate(args: Namespace) -> None:
    """Validate rows in a CSV file and report errors to stdout."""
    validators = _build_validators(args)
    if not validators:
        print("No validators specified. Use --required, --numeric, etc.",
              file=sys.stderr)
        sys.exit(1)

    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()

    invalid_count = 0
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=["row", "column_errors"],
        lineterminator="\n",
    )
    writer.writeheader()

    for idx, (row, errors) in enumerate(validate_rows(rows, validators), start=1):
        if errors:
            writer.writerow({"row": idx, "column_errors": " | ".join(errors)})
            invalid_count += 1

    print(f"\nValidation complete: {invalid_count} invalid row(s) found.",
          file=sys.stderr)
    if invalid_count > 0 and args.strict:
        sys.exit(2)


def register(subparsers) -> None:
    """Register the *validate* sub-command on *subparsers*."""
    p: ArgumentParser = subparsers.add_parser(
        "validate",
        help="Validate rows in a CSV file against specified rules.",
    )
    p.add_argument("input", help="Path to input CSV file")
    p.add_argument(
        "--required", nargs="+", metavar="COL",
        help="Columns that must be non-empty",
    )
    p.add_argument(
        "--numeric", nargs="+", metavar="COL",
        help="Columns that must contain numeric values",
    )
    p.add_argument(
        "--max-length", nargs="+", metavar="COL:N",
        help="Columns with max character length (format: col:n)",
    )
    p.add_argument(
        "--one-of", nargs="+", metavar="COL:V1,V2",
        help="Columns restricted to a set of values (format: col:v1,v2,...)",
    )
    p.add_argument(
        "--strict", action="store_true",
        help="Exit with code 2 if any invalid rows are found",
    )
    p.set_defaults(func=cmd_validate)
