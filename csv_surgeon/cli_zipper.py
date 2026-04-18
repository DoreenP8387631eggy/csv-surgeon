"""CLI commands for zip/unzip column operations."""
import argparse
import sys
import csv
from csv_surgeon.zipper import zip_columns, unzip_column


def cmd_zip(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = zip_columns(
        reader,
        col_a=args.col_a,
        col_b=args.col_b,
        output_col=args.output,
        separator=args.sep,
        drop_originals=args.drop,
    )
    rows = list(rows)
    if not rows:
        args.output_file.write("")
        return
    writer = csv.DictWriter(args.output_file, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def cmd_unzip(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    output_cols = [c.strip() for c in args.output_cols.split(",")]
    rows = unzip_column(
        reader,
        col=args.col,
        output_cols=output_cols,
        separator=args.sep,
        drop_original=args.drop,
    )
    rows = list(rows)
    if not rows:
        args.output_file.write("")
        return
    writer = csv.DictWriter(args.output_file, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def register(subparsers) -> None:
    p_zip = subparsers.add_parser("zip", help="Combine two columns into one")
    p_zip.add_argument("input", type=argparse.FileType("r"))
    p_zip.add_argument("--col-a", required=True)
    p_zip.add_argument("--col-b", required=True)
    p_zip.add_argument("--output", required=True)
    p_zip.add_argument("--sep", default="|")
    p_zip.add_argument("--drop", action="store_true")
    p_zip.add_argument("--output-file", type=argparse.FileType("w"), default=sys.stdout)
    p_zip.set_defaults(func=cmd_zip)

    p_unzip = subparsers.add_parser("unzip", help="Split one column into multiple")
    p_unzip.add_argument("input", type=argparse.FileType("r"))
    p_unzip.add_argument("--col", required=True)
    p_unzip.add_argument("--output-cols", required=True, help="Comma-separated output column names")
    p_unzip.add_argument("--sep", default="|")
    p_unzip.add_argument("--drop", action="store_true")
    p_unzip.add_argument("--output-file", type=argparse.FileType("w"), default=sys.stdout)
    p_unzip.set_defaults(func=cmd_unzip)
