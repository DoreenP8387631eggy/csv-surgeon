"""cli_censor.py – CLI sub-command for censoring column values."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon.censor import (
    censor_column,
    censor_columns,
    censor_pattern,
)


def cmd_censor(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    if args.pattern:
        rows = censor_pattern(
            rows,
            args.column,
            args.pattern,
            replacement=args.replacement,
        )
    elif args.columns:
        all_cols = [args.column] + args.columns
        rows = censor_columns(rows, all_cols, replacement=args.replacement)
    else:
        rows = censor_column(rows, args.column, replacement=args.replacement)

    rows = list(rows)
    if not rows:
        args.output.write("")
        return

    writer = csv.DictWriter(args.output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def register(subparsers) -> None:
    p = subparsers.add_parser("censor", help="Redact column values")
    p.add_argument("column", help="Primary column to censor")
    p.add_argument(
        "--columns",
        nargs="*",
        default=[],
        help="Additional columns to censor (combined with primary column)",
    )
    p.add_argument(
        "--pattern",
        default=None,
        help="Regex pattern; matching substrings are replaced",
    )
    p.add_argument(
        "--replacement",
        default="***",
        help="Replacement string (default: ***)",
    )
    p.add_argument(
        "--input",
        type=argparse.FileType("r"),
        default=sys.stdin,
    )
    p.add_argument(
        "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    p.set_defaults(func=cmd_censor)
