"""Command-line interface for csv-surgeon.

Provides a CLI entry point for performing filter, transform, and aggregation
operations on CSV files via subcommands.
"""

import argparse
import sys
from pathlib import Path

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon import filters as F
from csv_surgeon import transform as T
from csv_surgeon import aggregator as A


def build_filter_pipeline(filter_args: list[str]) -> FilterPipeline:
    """Parse filter expressions and build a FilterPipeline.

    Each filter expression has the form: <column><op><value>
    Supported operators: =, !=, ~  (contains)

    Examples:
        name=Alice
        age!=30
        city~York
    """
    pipeline = FilterPipeline()
    for expr in filter_args:
        if "!=" in expr:
            col, val = expr.split("!=", 1)
            pipeline.add_filter(F.not_equals(col.strip(), val.strip()))
        elif "~" in expr:
            col, val = expr.split("~", 1)
            pipeline.add_filter(F.contains(col.strip(), val.strip()))
        elif "=" in expr:
            col, val = expr.split("=", 1)
            pipeline.add_filter(F.equals(col.strip(), val.strip()))
        else:
            print(f"Warning: unrecognised filter expression '{expr}', skipping.", file=sys.stderr)
    return pipeline


def cmd_filter(args: argparse.Namespace) -> int:
    """Execute the 'filter' subcommand: filter rows and write to output."""
    pipeline = build_filter_pipeline(args.filter or [])

    reader = StreamingCSVReader(args.input)
    output_path = args.output or "-"
    writer = StreamingCSVWriter(output_path)

    filtered = pipeline.apply(reader.iter_rows())
    writer.write_rows(filtered, headers=reader.headers)

    print(f"Rows written: {writer.rows_written}", file=sys.stderr)
    return 0


def cmd_aggregate(args: argparse.Namespace) -> int:
    """Execute the 'aggregate' subcommand: print summary statistics."""
    reader = StreamingCSVReader(args.input)
    rows = list(reader.iter_rows())

    op = args.operation
    col = args.column

    ops = {
        "count": lambda: A.count(iter(rows), col if col else None),
        "sum": lambda: A.sum_column(iter(rows), col),
        "min": lambda: A.min_column(iter(rows), col),
        "max": lambda: A.max_column(iter(rows), col),
        "average": lambda: A.average_column(iter(rows), col),
    }

    if op not in ops:
        print(f"Unknown operation '{op}'. Choose from: {', '.join(ops)}", file=sys.stderr)
        return 1

    if op != "count" and not col:
        print(f"Operation '{op}' requires --column.", file=sys.stderr)
        return 1

    result = ops[op]()
    print(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the top-level argument parser."""
    parser = argparse.ArgumentParser(
        prog="csv-surgeon",
        description="Perform complex transformations and filtering on large CSV files.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- filter subcommand ---
    filter_parser = subparsers.add_parser("filter", help="Filter rows in a CSV file.")
    filter_parser.add_argument("input", type=Path, help="Path to input CSV file.")
    filter_parser.add_argument("-o", "--output", type=Path, default=None,
                               help="Path to output CSV file (default: stdout).")
    filter_parser.add_argument("-f", "--filter", action="append", metavar="EXPR",
                               help="Filter expression, e.g. 'age=30' or 'name~Alice'. Repeatable.")
    filter_parser.set_defaults(func=cmd_filter)

    # --- aggregate subcommand ---
    agg_parser = subparsers.add_parser("aggregate", help="Compute aggregate statistics on a CSV column.")
    agg_parser.add_argument("input", type=Path, help="Path to input CSV file.")
    agg_parser.add_argument("operation", choices=["count", "sum", "min", "max", "average"],
                            help="Aggregation operation to perform.")
    agg_parser.add_argument("-c", "--column", default=None,
                            help="Column name to aggregate (required for sum/min/max/average).")
    agg_parser.set_defaults(func=cmd_aggregate)

    return parser


def main() -> None:
    """Main entry point for the csv-surgeon CLI."""
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
