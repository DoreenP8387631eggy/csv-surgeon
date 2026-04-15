"""CLI sub-command for column normalization."""

import argparse
import csv
import sys

from csv_surgeon.normalizer import (
    strip_whitespace,
    normalize_whitespace,
    to_lowercase,
    to_titlecase,
    remove_non_alphanumeric,
    fill_empty,
)
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


_OPERATIONS = {
    "strip": strip_whitespace,
    "normalize-ws": normalize_whitespace,
    "lowercase": to_lowercase,
    "titlecase": to_titlecase,
    "remove-symbols": remove_non_alphanumeric,
    "fill-empty": fill_empty,
}


def cmd_normalize(args: argparse.Namespace) -> None:
    """Apply normalization transforms to one or more columns."""
    if not args.ops:
        print("error: at least one --op OPERATION:COLUMN is required", file=sys.stderr)
        sys.exit(1)

    transforms = []
    for spec in args.ops:
        parts = spec.split(":", 1)
        if len(parts) != 2:
            print(f"error: invalid op spec '{spec}', expected OPERATION:COLUMN", file=sys.stderr)
            sys.exit(1)
        op_name, column = parts
        if op_name not in _OPERATIONS:
            print(f"error: unknown operation '{op_name}'. choices: {list(_OPERATIONS)}", file=sys.stderr)
            sys.exit(1)
        if op_name == "fill-empty":
            transforms.append(_OPERATIONS[op_name](column, default=args.default or ""))
        else:
            transforms.append(_OPERATIONS[op_name](column))

    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()
    for transform in transforms:
        rows = transform(rows)

    writer = StreamingCSVWriter(args.output)
    writer.write_rows(reader.headers, rows)


def register(subparsers) -> None:
    parser = subparsers.add_parser("normalize", help="Normalize column values")
    parser.add_argument("input", help="Input CSV file")
    parser.add_argument("output", help="Output CSV file")
    parser.add_argument(
        "--op",
        dest="ops",
        action="append",
        metavar="OPERATION:COLUMN",
        help=(
            "Normalization operation and target column. "
            f"Available operations: {list(_OPERATIONS)}. "
            "Can be specified multiple times."
        ),
    )
    parser.add_argument(
        "--default",
        default="",
        help="Default value used by fill-empty (default: empty string)",
    )
    parser.set_defaults(func=cmd_normalize)
