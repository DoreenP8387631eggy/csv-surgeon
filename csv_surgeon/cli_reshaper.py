"""CLI commands for column reshaping."""
import argparse
import sys
import csv
from csv_surgeon.reshaper import reorder_columns, select_columns, drop_columns


def cmd_reshape(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    if args.select:
        cols = [c.strip() for c in args.select.split(",")]
        rows = select_columns(rows, cols)
        fieldnames = cols
    elif args.drop:
        cols = [c.strip() for c in args.drop.split(",")]
        rows = drop_columns(rows, cols)
        fieldnames = [f for f in (reader.fieldnames or []) if f not in cols]
    elif args.order:
        cols = [c.strip() for c in args.order.split(",")]
        rows = reorder_columns(rows, cols)
        fieldnames = cols
    else:
        print("error: one of --select, --drop, or --order is required", file=sys.stderr)
        sys.exit(1)

    writer = csv.DictWriter(args.output, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in fieldnames})


def register(subparsers) -> None:
    p = subparsers.add_parser("reshape", help="Reorder, select, or drop columns")
    p.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", "-o", type=argparse.FileType("w"), default=sys.stdout)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--select", help="Comma-separated columns to keep")
    group.add_argument("--drop", help="Comma-separated columns to remove")
    group.add_argument("--order", help="Comma-separated column order")
    p.set_defaults(func=cmd_reshape)
