"""CLI commands for the annotator module."""
import argparse
import sys
import csv
from csv_surgeon.annotator import (
    annotate_row_number,
    annotate_source,
    annotate_hash,
    annotate_is_empty,
)
from csv_surgeon.writer import StreamingCSVWriter


def cmd_annotate(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    if args.mode == "row_number":
        rows = annotate_row_number(rows, output_col=args.output_col, start=args.start)
    elif args.mode == "source":
        rows = annotate_source(rows, source=args.source, output_col=args.output_col)
    elif args.mode == "hash":
        cols = args.columns.split(",") if args.columns else None
        rows = annotate_hash(rows, columns=cols, output_col=args.output_col, algorithm=args.algorithm)
    elif args.mode == "is_empty":
        if not args.column:
            print("--column is required for is_empty mode", file=sys.stderr)
            sys.exit(1)
        rows = annotate_is_empty(rows, column=args.column, output_col=args.output_col)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    writer = StreamingCSVWriter(args.output)
    writer.write_rows(rows)


def register(subparsers) -> None:
    p = subparsers.add_parser("annotate", help="Annotate rows with metadata")
    p.add_argument("input", type=argparse.FileType("r"), help="Input CSV")
    p.add_argument("output", type=argparse.FileType("w"), help="Output CSV")
    p.add_argument(
        "--mode",
        choices=["row_number", "source", "hash", "is_empty"],
        required=True,
    )
    p.add_argument("--output-col", dest="output_col", default=None)
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--source", default="")
    p.add_argument("--columns", default=None, help="Comma-separated columns for hash")
    p.add_argument("--algorithm", default="md5")
    p.add_argument("--column", default=None, help="Column to check for is_empty")
    p.set_defaults(
        func=cmd_annotate,
        output_col="_annotation",
    )
