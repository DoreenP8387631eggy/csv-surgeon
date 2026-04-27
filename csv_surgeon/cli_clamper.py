"""CLI command for string-length clamping."""
import argparse
import csv
import sys

from csv_surgeon.clamper import clamp_length


def cmd_clamp_length(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = clamp_length(
        iter(reader),
        col=args.column,
        min_len=args.min_len,
        max_len=args.max_len,
        pad_char=args.pad_char,
        pad_right=not args.pad_left,
        suffix=args.suffix,
    )

    first = next(rows, None)
    if first is None:
        return

    writer = csv.DictWriter(args.output, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(rows)


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "clamp-length",
        help="Clamp string length of a column (pad short, truncate long)",
    )
    p.add_argument("column", help="Column to clamp")
    p.add_argument("--min-len", type=int, default=None, help="Minimum string length")
    p.add_argument("--max-len", type=int, default=None, help="Maximum string length")
    p.add_argument(
        "--pad-char", default=" ", help="Character used for padding (default: space)"
    )
    p.add_argument(
        "--pad-left",
        action="store_true",
        help="Pad on the left instead of the right",
    )
    p.add_argument(
        "--suffix",
        default="",
        help="Suffix appended when truncating (e.g. '...')",
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
    p.set_defaults(func=cmd_clamp_length)
