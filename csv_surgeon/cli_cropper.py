"""CLI commands for the cropper module."""
import argparse
import csv
import sys
from csv_surgeon import cropper


def cmd_crop(args):
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    op = args.operation
    col = args.column
    chars = args.chars or None

    if op == "strip":
        rows = cropper.strip_column(rows, col, chars)
    elif op == "lstrip":
        rows = cropper.lstrip_column(rows, col, chars)
    elif op == "rstrip":
        rows = cropper.rstrip_column(rows, col, chars)
    elif op == "remove-prefix":
        if not args.chars:
            print("--chars required for remove-prefix", file=sys.stderr)
            sys.exit(1)
        rows = cropper.remove_prefix(rows, col, args.chars)
    elif op == "remove-suffix":
        if not args.chars:
            print("--chars required for remove-suffix", file=sys.stderr)
            sys.exit(1)
        rows = cropper.remove_suffix(rows, col, args.chars)
    else:
        print(f"Unknown operation: {op}", file=sys.stderr)
        sys.exit(1)

    rows = list(rows)
    if not rows:
        return

    writer = csv.DictWriter(args.output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)


def register(subparsers):
    p = subparsers.add_parser("crop", help="Strip or remove prefixes/suffixes from a column")
    p.add_argument("--input", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("--column", required=True, help="Column to crop")
    p.add_argument(
        "--operation",
        choices=["strip", "lstrip", "rstrip", "remove-prefix", "remove-suffix"],
        default="strip",
    )
    p.add_argument("--chars", default=None, help="Characters or string to remove")
    p.set_defaults(func=cmd_crop)
