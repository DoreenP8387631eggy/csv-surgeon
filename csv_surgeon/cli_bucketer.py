"""CLI commands for bucketing/binning a numeric column."""
import argparse
import sys
import csv
from csv_surgeon.bucketer import bucket_column


def cmd_bucket(args: argparse.Namespace) -> None:
    edges = [float(e) for e in args.edges.split(",")]
    labels = [l.strip() for l in args.labels.split(",")] if args.labels else None

    reader = csv.DictReader(args.input)
    rows = bucket_column(
        iter(reader),
        column=args.column,
        edges=edges,
        labels=labels,
        output_column=args.output_column,
        default=args.default,
    )

    first = next(rows, None)
    if first is None:
        return
    writer = csv.DictWriter(args.output, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(rows)


def register(subparsers) -> None:
    p = subparsers.add_parser("bucket", help="Bin a numeric column into labelled buckets")
    p.add_argument("--input", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("--column", required=True, help="Numeric column to bin")
    p.add_argument("--edges", required=True, help="Comma-separated bin edges e.g. 0,33,66,100")
    p.add_argument("--labels", default=None, help="Comma-separated bucket labels (optional)")
    p.add_argument("--output-column", default="bucket", dest="output_column")
    p.add_argument("--default", default="", help="Value for non-numeric or out-of-range rows")
    p.set_defaults(func=cmd_bucket)
