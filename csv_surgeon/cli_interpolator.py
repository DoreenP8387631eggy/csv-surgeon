"""CLI subcommand: interpolate missing values in a column."""
import argparse
import csv
import sys

from csv_surgeon.interpolator import interpolate_column, ffill_column, bfill_column


def cmd_interpolate(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    if not reader.fieldnames:
        print("error: empty or missing CSV headers", file=sys.stderr)
        sys.exit(1)

    method = args.method
    column = args.column
    fill_value = args.fill_value

    if method == "linear":
        transform = interpolate_column(column, method="linear", fill_value=fill_value)
    elif method == "ffill":
        transform = ffill_column(column, fill_value=fill_value)
    elif method == "bfill":
        transform = bfill_column(column, fill_value=fill_value)
    else:
        print(f"error: unknown method '{method}'", file=sys.stderr)
        sys.exit(1)

    rows = (dict(r) for r in reader)
    result = list(transform(rows))

    if not result:
        writer = csv.DictWriter(args.output, fieldnames=reader.fieldnames)
        writer.writeheader()
        return

    writer = csv.DictWriter(args.output, fieldnames=result[0].keys())
    writer.writeheader()
    writer.writerows(result)


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "interpolate",
        help="Fill missing values in a column via interpolation.",
    )
    p.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("-o", "--output", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("-c", "--column", required=True, help="Column to interpolate.")
    p.add_argument(
        "-m",
        "--method",
        choices=["linear", "ffill", "bfill"],
        default="linear",
        help="Interpolation method (default: linear).",
    )
    p.add_argument(
        "--fill-value",
        default="",
        dest="fill_value",
        help="Fallback value when no neighbour exists (default: empty string).",
    )
    p.set_defaults(func=cmd_interpolate)
