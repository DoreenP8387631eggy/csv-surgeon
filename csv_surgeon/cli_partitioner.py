"""CLI command: csv-surgeon partition"""
import argparse
import csv
import os
import sys
from csv_surgeon.partitioner import partition_by_column


def cmd_partition(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    if not reader.fieldnames:
        print("error: empty input", file=sys.stderr)
        sys.exit(1)

    buckets = partition_by_column(reader, args.column)

    os.makedirs(args.outdir, exist_ok=True)
    for label, rows in buckets.items():
        safe = label.replace(os.sep, "_") or "__empty__"
        path = os.path.join(args.outdir, f"{safe}.csv")
        with open(path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(reader.fieldnames))
            writer.writeheader()
            writer.writerows(rows)
        print(f"  wrote {len(rows)} rows -> {path}")


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("partition", help="Split CSV into files by column value")
    p.add_argument("input", type=argparse.FileType("r"), default="-", nargs="?")
    p.add_argument("--column", required=True, help="Column to partition on")
    p.add_argument("--outdir", default="partitions", help="Output directory")
    p.set_defaults(func=cmd_partition)
