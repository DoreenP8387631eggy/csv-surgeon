"""CLI commands for the compactor module."""
import argparse
import csv
import sys
from csv_surgeon.compactor import compact_columns, compact_first_valid, drop_empty_columns


def cmd_compact(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    columns = [c.strip() for c in args.columns.split(",")]

    if args.mode == "join":
        rows = compact_columns(
            reader,
            columns=columns,
            output_col=args.output_col,
            separator=args.separator,
            skip_empty=not args.keep_empty,
        )
    elif args.mode == "first":
        rows = compact_first_valid(
            reader,
            columns=columns,
            output_col=args.output_col,
            default=args.default,
        )
    elif args.mode == "drop-empty":
        rows = drop_empty_columns(reader, columns=columns)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    rows = list(rows)
    if not rows:
        return
    writer = csv.DictWriter(args.output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("compact", help="Compact sparse columns into one")
    p.add_argument("--columns", required=True, help="Comma-separated column names")
    p.add_argument("--mode", choices=["join", "first", "drop-empty"], default="join")
    p.add_argument("--output-col", default="compacted")
    p.add_argument("--separator", default=",")
    p.add_argument("--default", default="")
    p.add_argument("--keep-empty", action="store_true")
    p.add_argument("input", type=argparse.FileType("r"), default="-", nargs="?")
    p.add_argument("output", type=argparse.FileType("w"), default="-", nargs="?")
    p.set_defaults(func=cmd_compact)
