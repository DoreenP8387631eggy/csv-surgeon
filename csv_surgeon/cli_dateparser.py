"""CLI commands for date parsing/formatting."""
from __future__ import annotations
import argparse
import sys
import csv
from csv_surgeon.dateparser import parse_date_column, format_date_column, extract_date_part


def cmd_date(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = list(reader)

    if args.action == "parse":
        result = parse_date_column(
            rows,
            column=args.column,
            output_column=args.output_column,
            default=args.default,
        )
    elif args.action == "format":
        result = format_date_column(
            rows,
            column=args.column,
            output_format=args.output_format,
            output_column=args.output_column,
            default=args.default,
        )
    elif args.action == "extract":
        result = extract_date_part(
            rows,
            column=args.column,
            part=args.part,
            output_column=args.output_column,
            default=args.default,
        )
    else:
        print(f"Unknown action: {args.action}", file=sys.stderr)
        sys.exit(1)

    result_list = list(result)
    if not result_list:
        return
    writer = csv.DictWriter(args.output, fieldnames=list(result_list[0].keys()))
    writer.writeheader()
    writer.writerows(result_list)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("date", help="Parse, format or extract date parts from a column")
    p.add_argument("input", type=argparse.FileType("r"), default="-")
    p.add_argument("--action", choices=["parse", "format", "extract"], required=True)
    p.add_argument("--column", required=True)
    p.add_argument("--output-column", dest="output_column", default=None)
    p.add_argument("--output-format", dest="output_format", default="%Y-%m-%d")
    p.add_argument("--part", choices=["year", "month", "day", "weekday", "quarter"], default="year")
    p.add_argument("--default", default="")
    p.add_argument("--output", type=argparse.FileType("w"), default="-")
    p.set_defaults(func=cmd_date)
