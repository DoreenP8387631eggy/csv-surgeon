"""Command-line interface for csv-surgeon."""

from __future__ import annotations

import argparse
import sys

from csv_surgeon.filters import (
    equals, not_equals, contains, greater_than, less_than,
)
from csv_surgeon.pipeline import FilterPipeline
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.aggregator import count, sum_column, min_column, max_column, average_column
from csv_surgeon.joiner import inner_join, left_join
from csv_surgeon.sorter import sort_rows, sort_rows_multi


def build_filter_pipeline(args) -> FilterPipeline:
    pipeline = FilterPipeline()
    for raw in getattr(args, "filter", []) or []:
        col, op, val = raw.split(":", 2)
        dispatch = {
            "eq": equals, "ne": not_equals,
            "contains": contains, "gt": greater_than, "lt": less_than,
        }
        if op not in dispatch:
            raise ValueError(f"Unknown filter op: {op}")
        pipeline.add_filter(dispatch[op](col, val))
    return pipeline


def cmd_filter(args) -> None:
    pipeline = build_filter_pipeline(args)
    reader = StreamingCSVReader(args.input)
    writer = StreamingCSVWriter(args.output)
    rows = pipeline.apply(reader.iter_rows())
    writer.write_rows(rows, headers=reader.headers)


def cmd_aggregate(args) -> None:
    reader = StreamingCSVReader(args.input)
    rows = list(reader.iter_rows())
    fn_map = {
        "count": lambda: count(rows, args.column or None),
        "sum": lambda: sum_column(rows, args.column),
        "min": lambda: min_column(rows, args.column),
        "max": lambda: max_column(rows, args.column),
        "avg": lambda: average_column(rows, args.column),
    }
    result = fn_map[args.func]()
    print(result)


def cmd_join(args) -> None:
    left_reader = StreamingCSVReader(args.left)
    right_reader = StreamingCSVReader(args.right)
    left_rows = list(left_reader.iter_rows())
    right_rows = list(right_reader.iter_rows())
    join_fn = inner_join if args.type == "inner" else left_join
    result = join_fn(left_rows, right_rows, args.key)
    if result:
        writer = StreamingCSVWriter(args.output)
        writer.write_rows(iter(result), headers=list(result[0].keys()))


def cmd_sort(args) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()
    if args.keys:
        key_specs = []
        for spec in args.keys:
            parts = spec.split(":")
            col = parts[0]
            rev = len(parts) > 1 and parts[1].lower() == "desc"
            key_specs.append((col, rev))
        sorted_rows = sort_rows_multi(rows, keys=key_specs, numeric=args.numeric)
    else:
        sorted_rows = sort_rows(
            rows, key=args.key, reverse=args.reverse, numeric=args.numeric
        )
    writer = StreamingCSVWriter(args.output)
    writer.write_rows(sorted_rows, headers=reader.headers)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="csv-surgeon")
    sub = parser.add_subparsers(dest="command")

    # filter
    p_filter = sub.add_parser("filter")
    p_filter.add_argument("input")
    p_filter.add_argument("output")
    p_filter.add_argument("--filter", action="append")

    # aggregate
    p_agg = sub.add_parser("aggregate")
    p_agg.add_argument("input")
    p_agg.add_argument("func", choices=["count", "sum", "min", "max", "avg"])
    p_agg.add_argument("--column")

    # join
    p_join = sub.add_parser("join")
    p_join.add_argument("left")
    p_join.add_argument("right")
    p_join.add_argument("output")
    p_join.add_argument("--key", required=True)
    p_join.add_argument("--type", choices=["inner", "left"], default="inner")

    # sort
    p_sort = sub.add_parser("sort")
    p_sort.add_argument("input")
    p_sort.add_argument("output")
    p_sort.add_argument("--key", default="", help="Single column to sort by")
    p_sort.add_argument(
        "--keys", nargs="+",
        help="Multi-column sort specs: col[:asc|desc] ..."
    )
    p_sort.add_argument("--reverse", action="store_true")
    p_sort.add_argument("--numeric", action="store_true")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {
        "filter": cmd_filter,
        "aggregate": cmd_aggregate,
        "join": cmd_join,
        "sort": cmd_sort,
    }
    if args.command not in dispatch:
        parser.print_help()
        sys.exit(1)
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
