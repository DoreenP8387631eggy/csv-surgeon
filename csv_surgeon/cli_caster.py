"""CLI command for casting column types in a CSV file."""

import argparse
import csv
import sys

from csv_surgeon.caster import cast_columns
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def cmd_cast(args: argparse.Namespace) -> None:
    """Cast one or more CSV columns to a specified type and write the result."""
    if not args.cast:
        print("Error: at least one --cast COLUMN:TYPE argument is required.", file=sys.stderr)
        sys.exit(1)

    mapping: dict[str, str] = {}
    for spec in args.cast:
        if ":" not in spec:
            print(f"Error: invalid cast spec {spec!r}. Expected COLUMN:TYPE.", file=sys.stderr)
            sys.exit(1)
        col, typ = spec.split(":", 1)
        mapping[col.strip()] = typ.strip()

    reader = StreamingCSVReader(args.input)
    transform = cast_columns(mapping)

    output = open(args.output, "w", newline="") if args.output else sys.stdout
    try:
        rows = reader.iter_rows()
        casted = transform(rows)
        writer = StreamingCSVWriter(output, fieldnames=reader.headers)
        writer.write_rows(casted)
    finally:
        if args.output:
            output.close()


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "cast",
        help="Cast CSV column values to a specified type (int, float, bool, str).",
    )
    parser.add_argument("input", help="Path to the input CSV file.")
    parser.add_argument(
        "--cast",
        metavar="COLUMN:TYPE",
        action="append",
        required=True,
        help="Column and target type, e.g. --cast age:int --cast score:float.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        default=None,
        help="Write output to FILE instead of stdout.",
    )
    parser.set_defaults(func=cmd_cast)
