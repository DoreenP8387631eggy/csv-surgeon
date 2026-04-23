"""CLI sub-commands for the hasher module."""

import argparse
import csv
import sys
from typing import Optional

from csv_surgeon.hasher import hash_column, hash_row, truncate_hash


def cmd_hash(args: argparse.Namespace) -> None:
    """Entry-point for the ``csv-surgeon hash`` sub-command."""
    reader = csv.DictReader(args.input)

    if args.mode == "column":
        if not args.column:
            print("error: --column is required for column mode", file=sys.stderr)
            sys.exit(1)
        transform = hash_column(
            column=args.column,
            algorithm=args.algorithm,
            output_col=args.output_col or None,
            secret=args.secret or None,
        )
    elif args.mode == "row":
        cols = args.columns.split(",") if args.columns else None
        transform = hash_row(
            columns=cols,
            algorithm=args.algorithm,
            output_col=args.output_col or "row_hash",
            separator=args.separator,
        )
    else:
        print(f"error: unknown mode '{args.mode}'", file=sys.stderr)
        sys.exit(1)

    rows = list(reader)
    if not rows:
        return

    transformed = [transform(r) for r in rows]

    if args.truncate and args.truncate > 0:
        out_key = args.output_col or (
            f"{args.column}_hash" if args.mode == "column" else "row_hash"
        )
        shorten = truncate_hash(out_key, length=args.truncate)
        transformed = [shorten(r) for r in transformed]

    writer = csv.DictWriter(args.output, fieldnames=list(transformed[0].keys()))
    writer.writeheader()
    writer.writerows(transformed)


def register(subparsers) -> None:
    p = subparsers.add_parser("hash", help="Hash column values")
    p.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("-o", "--output", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument(
        "--mode",
        choices=["column", "row"],
        default="column",
        help="Hash a single column or a composite row key (default: column)",
    )
    p.add_argument("--column", help="Column to hash (column mode)")
    p.add_argument("--columns", help="Comma-separated columns for row mode")
    p.add_argument("--algorithm", default="sha256", help="Hash algorithm (default: sha256)")
    p.add_argument("--output-col", dest="output_col", help="Output column name")
    p.add_argument("--secret", help="HMAC secret key")
    p.add_argument("--separator", default="|", help="Separator for row mode (default: |)")
    p.add_argument(
        "--truncate",
        type=int,
        default=0,
        help="Truncate digest to N characters (0 = no truncation)",
    )
    p.set_defaults(func=cmd_hash)
