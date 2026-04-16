"""CLI commands for column formatting."""
import argparse
import sys
import csv
from csv_surgeon.formatter import format_column, zero_pad, number_format, date_reformat
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def cmd_format(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()

    if args.mode == "template":
        if not args.template:
            print("--template required for template mode", file=sys.stderr)
            sys.exit(1)
        transform = format_column(args.column, args.template)
    elif args.mode == "zeropad":
        transform = zero_pad(args.column, args.width)
    elif args.mode == "number":
        transform = number_format(args.column, decimals=args.decimals, thousands_sep=args.thousands)
    elif args.mode == "date":
        if not args.from_fmt or not args.to_fmt:
            print("--from-fmt and --to-fmt required for date mode", file=sys.stderr)
            sys.exit(1)
        transform = date_reformat(args.column, args.from_fmt, args.to_fmt)
    else:
        print(f"Unknown format mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    transformed = transform(rows)
    writer = StreamingCSVWriter(args.output, fieldnames=reader.headers)
    writer.write_rows(transformed)


def register(subparsers) -> None:
    p = subparsers.add_parser("format", help="Format column values")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to format")
    p.add_argument(
        "--mode",
        required=True,
        choices=["template", "zeropad", "number", "date"],
        help="Formatting mode",
    )
    p.add_argument("--template", default=None, help="Format template with {value} placeholder")
    p.add_argument("--width", type=int, default=5, help="Pad width for zeropad mode")
    p.add_argument("--decimals", type=int, default=2, help="Decimal places for number mode")
    p.add_argument("--thousands", action="store_true", help="Use thousands separator in number mode")
    p.add_argument("--from-fmt", dest="from_fmt", default=None, help="Input date format")
    p.add_argument("--to-fmt", dest="to_fmt", default=None, help="Output date format")
    p.set_defaults(func=cmd_format)
