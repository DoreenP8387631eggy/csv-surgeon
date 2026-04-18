"""CLI commands for windowing operations (rolling stats, lag, lead)."""
import argparse
import sys
import csv
from csv_surgeon.windower import rolling_mean, rolling_sum, lag_column, lead_column


def cmd_window(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    op = args.operation
    col = args.column
    out_col = args.output_column or None
    fill = args.fill

    if op == "rolling_mean":
        result = rolling_mean(rows, col, args.window, output_column=out_col, fill=fill)
    elif op == "rolling_sum":
        result = rolling_sum(rows, col, args.window, output_column=out_col, fill=fill)
    elif op == "lag":
        result = lag_column(rows, col, periods=args.periods, output_column=out_col, fill=fill)
    elif op == "lead":
        result = lead_column(rows, col, periods=args.periods, output_column=out_col, fill=fill)
    else:
        print(f"Unknown operation: {op}", file=sys.stderr)
        sys.exit(1)

    first = next(result, None)
    if first is None:
        return

    # Validate that the specified column exists in the input
    if col not in first:
        print(f"Error: column '{col}' not found in input. Available columns: {', '.join(first.keys())}", file=sys.stderr)
        sys.exit(1)

    writer = csv.DictWriter(args.output, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(result)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("window", help="Rolling window and lag/lead column operations")
    p.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", "-o", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("--operation", "-op", required=True,
                   choices=["rolling_mean", "rolling_sum", "lag", "lead"])
    p.add_argument("--column", "-c", required=True, help="Column to operate on")
    p.add_argument("--window", "-w", type=int, default=3, help="Window size for rolling ops")
    p.add_argument("--periods", "-p", type=int, default=1, help="Periods for lag/lead")
    p.add_argument("--output-column", "-oc", default="", help="Name for the new column")
    p.add_argument("--fill", "-f", default="", help="Fill value for incomplete windows")
    p.set_defaults(func=cmd_window)
