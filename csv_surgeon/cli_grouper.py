"""CLI sub-command: group-by — group rows and emit per-group aggregates."""

import argparse
import csv
import sys
from typing import List

from csv_surgeon.grouper import (
    group_by,
    aggregate_groups,
    agg_count,
    agg_sum,
    agg_max,
    agg_min,
)


_AGG_BUILDERS = {
    "count": lambda col: agg_count(col if col else None),
    "sum":   lambda col: agg_sum(col),
    "max":   lambda col: agg_max(col),
    "min":   lambda col: agg_min(col),
}


def _parse_agg_spec(spec: str):
    """Parse 'output_col:func:source_col' or 'output_col:count' into (name, fn)."""
    parts = spec.split(":")
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            f"Invalid aggregation spec '{spec}'. "
            "Expected format: output_col:func[:source_col]"
        )
    out_col = parts[0]
    func_name = parts[1].lower()
    src_col = parts[2] if len(parts) > 2 else ""
    if func_name not in _AGG_BUILDERS:
        raise argparse.ArgumentTypeError(
            f"Unknown aggregation function '{func_name}'. "
            f"Choose from: {', '.join(_AGG_BUILDERS)}"
        )
    fn = _AGG_BUILDERS[func_name](src_col)
    return out_col, fn


def cmd_group(args: argparse.Namespace) -> None:
    """Execute the group-by command."""
    key_columns: List[str] = [c.strip() for c in args.key.split(",")]

    aggregations = {}
    for spec in (args.agg or []):
        out_col, fn = _parse_agg_spec(spec)
        aggregations[out_col] = fn

    # Default: count all rows if no aggregation supplied
    if not aggregations:
        aggregations["count"] = agg_count()

    reader = csv.DictReader(args.input)
    rows = list(reader)
    groups = group_by(rows, key_columns)

    result_rows = list(aggregate_groups(groups, key_columns, aggregations))
    if not result_rows:
        return

    fieldnames = list(result_rows[0].keys())
    writer = csv.DictWriter(args.output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(result_rows)


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "group-by",
        help="Group rows by column(s) and compute aggregates.",
    )
    p.add_argument("input",  nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("output", nargs="?", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument(
        "--key", required=True,
        help="Comma-separated column name(s) to group by.",
    )
    p.add_argument(
        "--agg", action="append", metavar="OUT:FUNC[:SRC]",
        help=(
            "Aggregation spec in the form output_col:func[:source_col]. "
            "func is one of: count, sum, max, min. "
            "May be repeated for multiple aggregations."
        ),
    )
    p.set_defaults(func=cmd_group)
