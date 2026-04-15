"""CLI subcommand for row range selection."""

import argparse
import csv
import sys

from csv_surgeon.ranger import slice_rows, skip_rows, limit_rows, rows_between


def cmd_range(args: argparse.Namespace) -> None:
    """Filter rows by positional range and write to output."""
    reader = csv.DictReader(args.input)
    if reader.fieldnames is None:
        print("error: input CSV has no headers", file=sys.stderr)
        sys.exit(1)

    fieldnames = list(reader.fieldnames)
    writer = csv.DictWriter(args.output, fieldnames=fieldnames)
    writer.writeheader()

    rows = iter(reader)

    if args.mode == "slice":
        rows = slice_rows(
            rows,
            start=args.start,
            stop=args.stop,
            step=args.step,
        )
    elif args.mode == "skip":
        rows = skip_rows(rows, n=args.n)
    elif args.mode == "limit":
        rows = limit_rows(rows, n=args.n)
    elif args.mode == "between":
        rows = rows_between(rows, start=args.start, stop=args.stop)
    else:
        print(f"error: unknown mode '{args.mode}'", file=sys.stderr)
        sys.exit(1)

    for row in rows:
        writer.writerow(row)


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'range' subcommand."""
    p = subparsers.add_parser(
        "range",
        help="Select rows by positional range (slice / skip / limit / between).",
    )
    p.add_argument("input", type=argparse.FileType("r"), help="Input CSV file")
    p.add_argument(
        "output",
        type=argparse.FileType("w"),
        nargs="?",
        default=sys.stdout,
        help="Output CSV file (default: stdout)",
    )
    p.add_argument(
        "--mode",
        choices=["slice", "skip", "limit", "between"],
        default="slice",
        help="Range mode (default: slice)",
    )
    p.add_argument("--start", type=int, default=0, help="Start index (inclusive, 0-based)")
    p.add_argument("--stop", type=int, default=None, help="Stop index (exclusive)")
    p.add_argument("--step", type=int, default=1, help="Step (slice mode only)")
    p.add_argument("--n", type=int, default=0, help="Row count (skip / limit modes)")
    p.set_defaults(func=cmd_range)
