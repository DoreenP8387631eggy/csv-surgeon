"""CLI entry point for csv-surgeon."""

import argparse
import sys
from typing import List

from csv_surgeon.aggregator import count, sum_column, min_column, max_column, average_column
from csv_surgeon.filters import equals, not_equals, contains, greater_than, less_than
from csv_surgeon.joiner import inner_join, left_join
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def build_filter_pipeline(filter_args: List[str]) -> FilterPipeline:
    pipeline = FilterPipeline()
    for f in filter_args or []:
        col, op, val = f.split(":", 2)
        if op == "eq":
            pipeline.add_filter(equals(col, val))
        elif op == "ne":
            pipeline.add_filter(not_equals(col, val))
        elif op == "contains":
            pipeline.add_filter(contains(col, val))
        elif op == "gt":
            pipeline.add_filter(greater_than(col, float(val)))
        elif op == "lt":
            pipeline.add_filter(less_than(col, float(val)))
        else:
            raise ValueError(f"Unknown filter operator: {op}")
    return pipeline


def cmd_filter(args: argparse.Namespace) -> None:
    pipeline = build_filter_pipeline(args.filter)
    reader = StreamingCSVReader(args.input)
    writer = StreamingCSVWriter(args.output)
    rows = pipeline.apply(reader.iter_rows())
    writer.write_rows(rows, headers=reader.headers)
    print(f"Wrote {writer.rows_written} rows.", file=sys.stderr)


def cmd_aggregate(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = list(reader.iter_rows())
    op = args.operation
    col = args.column
    if op == "count":
        result = count(rows, col if col else None)
    elif op == "sum":
        result = sum_column(rows, col)
    elif op == "min":
        result = min_column(rows, col)
    elif op == "max":
        result = max_column(rows, col)
    elif op == "avg":
        result = average_column(rows, col)
    else:
        print(f"Unknown operation: {op}", file=sys.stderr)
        sys.exit(1)
    print(result)


def cmd_join(args: argparse.Namespace) -> None:
    left_reader = StreamingCSVReader(args.left)
    right_reader = StreamingCSVReader(args.right)
    right_rows = list(right_reader.iter_rows())
    join_fn = inner_join if args.join_type == "inner" else left_join
    merged = join_fn(
        left_reader.iter_rows(),
        right_rows,
        left_key=args.left_key,
        right_key=args.right_key or args.left_key,
        right_prefix=args.right_prefix,
    )
    writer = StreamingCSVWriter(args.output)
    writer.write_rows(merged)
    print(f"Wrote {writer.rows_written} rows.", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csv-surgeon", description="CSV transformation tool")
    sub = parser.add_subparsers(dest="command")

    f_parser = sub.add_parser("filter", help="Filter rows")
    f_parser.add_argument("input", help="Input CSV file")
    f_parser.add_argument("output", help="Output CSV file")
    f_parser.add_argument("--filter", action="append", metavar="COL:OP:VAL")

    a_parser = sub.add_parser("aggregate", help="Aggregate a column")
    a_parser.add_argument("input", help="Input CSV file")
    a_parser.add_argument("operation", choices=["count", "sum", "min", "max", "avg"])
    a_parser.add_argument("--column", default=None)

    j_parser = sub.add_parser("join", help="Join two CSV files")
    j_parser.add_argument("left", help="Left CSV file")
    j_parser.add_argument("right", help="Right CSV file")
    j_parser.add_argument("output", help="Output CSV file")
    j_parser.add_argument("--left-key", required=True, dest="left_key")
    j_parser.add_argument("--right-key", default=None, dest="right_key")
    j_parser.add_argument("--join-type", choices=["inner", "left"], default="inner", dest="join_type")
    j_parser.add_argument("--right-prefix", default="right_", dest="right_prefix")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "filter":
        cmd_filter(args)
    elif args.command == "aggregate":
        cmd_aggregate(args)
    elif args.command == "join":
        cmd_join(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
