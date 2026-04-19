"""CLI command for regex-based row splitting."""
import argparse
import csv
import sys

from csv_surgeon.splitter_regex import split_on_pattern, split_on_delimiter


def cmd_split_regex(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    if args.delimiter_mode:
        rows = split_on_delimiter(
            iter(reader),
            column=args.column,
            delimiter=args.sep,
            output_column=args.output_column or args.column,
            strip=not args.no_strip,
        )
    else:
        rows = split_on_pattern(
            iter(reader),
            column=args.column,
            pattern=args.pattern,
            output_column=args.output_column or args.column,
        )

    rows = list(rows)
    if not rows:
        return

    writer = csv.DictWriter(args.output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("split-regex", help="Split rows on regex pattern or delimiter")
    p.add_argument("--column", required=True, help="Column to split on")
    p.add_argument("--pattern", default="", help="Regex pattern to match")
    p.add_argument("--output-column", default=None, help="Output column name (default: same as column)")
    p.add_argument("--delimiter-mode", action="store_true", help="Split on a literal delimiter instead of regex")
    p.add_argument("--sep", default=",", help="Delimiter for delimiter mode")
    p.add_argument("--no-strip", action="store_true", help="Do not strip whitespace from split parts")
    p.add_argument("--input", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", type=argparse.FileType("w"), default=sys.stdout)
    p.set_defaults(func=cmd_split_regex)
