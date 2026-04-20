"""CLI command for routing CSV rows to separate output files."""
import argparse
import csv
import sys
from pathlib import Path
from typing import List

from csv_surgeon.router import build_rule, build_contains_rule, route_rows_stream
from csv_surgeon.reader import StreamingCSVReader


def _parse_rule(spec: str):
    """Parse 'label:column=value' or 'label:column~value' (contains)."""
    label, rest = spec.split(":", 1)
    if "~" in rest:
        column, value = rest.split("~", 1)
        return build_contains_rule(column, value, label)
    else:
        column, value = rest.split("=", 1)
        return build_rule(column, value, label)


def cmd_route(args: argparse.Namespace) -> None:
    rules = [_parse_rule(s) for s in args.rule]
    if not rules:
        print("Error: at least one --rule required.", file=sys.stderr)
        sys.exit(1)

    reader = StreamingCSVReader(args.input)
    headers = None
    writers = {}
    files = {}

    try:
        for label, row in route_rows_stream(reader.iter_rows(), rules, default_label=args.default):
            if headers is None:
                headers = list(row.keys())

            if label not in writers:
                out_path = Path(args.outdir) / f"{label}.csv"
                f = open(out_path, "w", newline="")
                files[label] = f
                w = csv.DictWriter(f, fieldnames=headers)
                w.writeheader()
                writers[label] = w

            writers[label].writerow(row)
    finally:
        for f in files.values():
            f.close()


def register(subparsers) -> None:
    p = subparsers.add_parser("route", help="Route rows to separate CSV files by rule")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("outdir", help="Output directory for routed files")
    p.add_argument("--rule", action="append", default=[], metavar="LABEL:COL=VAL",
                   help="Routing rule: 'label:col=val' or 'label:col~substr'")
    p.add_argument("--default", default="default", help="Label for unmatched rows")
    p.set_defaults(func=cmd_route)
