"""CLI commands for pivot and melt operations."""
import argparse
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.pivotter import pivot_rows, melt_rows


def cmd_pivot(args: argparse.Namespace) -> None:
    """Pivot a CSV: unique values of --pivot-col become new columns."""
    reader = StreamingCSVReader(args.input)
    rows = list(reader.iter_rows())
    if not rows:
        sys.stderr.write("Input file is empty.\n")
        sys.exit(1)

    result = pivot_rows(
        iter(rows),
        index_col=args.index_col,
        pivot_col=args.pivot_col,
        value_col=args.value_col,
    )
    if not result:
        sys.stderr.write("Pivot produced no output.\n")
        sys.exit(0)

    headers = list(result[0].keys())
    writer = StreamingCSVWriter(args.output, headers=headers)
    writer.write_rows(iter(result))


def cmd_melt(args: argparse.Namespace) -> None:
    """Melt (unpivot) a CSV: turn column headers into row values."""
    reader = StreamingCSVReader(args.input)
    id_cols = [c.strip() for c in args.id_cols.split(",")]
    value_cols = (
        [c.strip() for c in args.value_cols.split(",")]
        if args.value_cols
        else None
    )

    rows = reader.iter_rows()
    melted = melt_rows(
        rows,
        id_cols=id_cols,
        value_cols=value_cols,
        var_name=args.var_name,
        value_name=args.value_name,
    )

    first = next(melted, None)
    if first is None:
        sys.stderr.write("Melt produced no output.\n")
        sys.exit(0)

    headers = list(first.keys())
    writer = StreamingCSVWriter(args.output, headers=headers)
    import itertools
    writer.write_rows(itertools.chain([first], melted))


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    # pivot
    p_pivot = subparsers.add_parser("pivot", help="Pivot rows into columns")
    p_pivot.add_argument("input", help="Input CSV file")
    p_pivot.add_argument("output", help="Output CSV file")
    p_pivot.add_argument("--index-col", required=True, dest="index_col")
    p_pivot.add_argument("--pivot-col", required=True, dest="pivot_col")
    p_pivot.add_argument("--value-col", required=True, dest="value_col")
    p_pivot.set_defaults(func=cmd_pivot)

    # melt
    p_melt = subparsers.add_parser("melt", help="Melt columns into rows")
    p_melt.add_argument("input", help="Input CSV file")
    p_melt.add_argument("output", help="Output CSV file")
    p_melt.add_argument("--id-cols", required=True, dest="id_cols", help="Comma-separated id columns")
    p_melt.add_argument("--value-cols", default=None, dest="value_cols", help="Comma-separated columns to melt")
    p_melt.add_argument("--var-name", default="variable", dest="var_name")
    p_melt.add_argument("--value-name", default="value", dest="value_name")
    p_melt.set_defaults(func=cmd_melt)
