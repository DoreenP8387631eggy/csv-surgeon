"""CLI command for coalescing columns."""
import argparse
import sys
import csv
from csv_surgeon.coalescer import coalesce_columns, coalesce_fill
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def cmd_coalesce(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()
    columns = args.columns

    if args.fill:
        # fill mode: fill gaps in first column from the rest
        target, *fallbacks = columns
        transformed = coalesce_fill(rows, target, fallbacks)
    else:
        output_col = args.output or "coalesced"
        default = args.default or ""
        transformed = coalesce_columns(rows, columns, output_col, default=default)

    writer = StreamingCSVWriter(args.output_file if hasattr(args, "output_file") and args.output_file else sys.stdout)
    writer.write_rows(transformed)


def register(subparsers) -> None:
    p = subparsers.add_parser("coalesce", help="Coalesce multiple columns into one")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("columns", nargs="+", help="Columns to coalesce (in priority order)")
    p.add_argument("--output", help="Output column name (default: coalesced)")
    p.add_argument("--default", default="", help="Default value when all columns are empty")
    p.add_argument("--fill", action="store_true", help="Fill mode: fill first column from subsequent columns")
    p.add_argument("--output-file", dest="output_file", help="Write output to file instead of stdout")
    p.set_defaults(func=cmd_coalesce)
