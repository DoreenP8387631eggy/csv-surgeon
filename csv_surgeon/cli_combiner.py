"""cli_combiner.py – CLI sub-command for combining columns."""

import argparse
import sys
import csv

from csv_surgeon.combiner import combine_template, combine_columns


def cmd_combine(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = list(reader)

    if args.template:
        result = combine_template(
            rows,
            template=args.template,
            output_col=args.output_col,
            default=args.default,
        )
    else:
        if not args.columns:
            print("error: --columns or --template is required", file=sys.stderr)
            sys.exit(1)
        result = combine_columns(
            rows,
            columns=args.columns,
            output_col=args.output_col,
            separator=args.separator,
            skip_empty=not args.keep_empty,
        )

    result_list = list(result)
    if not result_list:
        return

    writer = csv.DictWriter(args.output, fieldnames=list(result_list[0].keys()))
    writer.writeheader()
    writer.writerows(result_list)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("combine", help="Combine multiple columns into one")
    p.add_argument("input", type=argparse.FileType("r"), default="-", nargs="?",
                   help="Input CSV (default: stdin)")
    p.add_argument("--output", "-o", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("--columns", "-c", nargs="+", metavar="COL")
    p.add_argument("--template", "-t", metavar="TEMPLATE")
    p.add_argument("--output-col", default="combined")
    p.add_argument("--separator", default=" ")
    p.add_argument("--default", default="")
    p.add_argument("--keep-empty", action="store_true")
    p.set_defaults(func=cmd_combine)
