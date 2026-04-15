"""CLI sub-command: merge — vertically stack multiple CSV files."""
import argparse
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.merger import merge_rows, merge_rows_strict


def cmd_merge(args: argparse.Namespace) -> None:
    """Merge two or more CSV files vertically and write to output.

    Args:
        args: Parsed CLI arguments with attributes:
            - inputs (List[str]): paths to input CSV files
            - output (str): path to output CSV file or '-' for stdout
            - strict (bool): raise on column mismatch when True
            - fill (str): fill value for missing columns
    """
    if len(args.inputs) < 2:
        print("error: merge requires at least two input files", file=sys.stderr)
        sys.exit(1)

    readers = [StreamingCSVReader(path) for path in args.inputs]
    streams = [reader.iter_rows() for reader in readers]

    try:
        if args.strict:
            merged = merge_rows_strict(streams)
        else:
            merged = merge_rows(streams, fill_value=args.fill)

        output_path = None if args.output == "-" else args.output
        writer = StreamingCSVWriter(output_path)
        writer.write_rows(merged)

    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'merge' sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "merge",
        help="Vertically stack multiple CSV files into one.",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        metavar="INPUT",
        help="Two or more input CSV file paths.",
    )
    parser.add_argument(
        "-o", "--output",
        default="-",
        metavar="OUTPUT",
        help="Output file path (default: stdout).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if column sets differ between files.",
    )
    parser.add_argument(
        "--fill",
        default="",
        metavar="VALUE",
        help="Fill value for missing columns (default: empty string).",
    )
    parser.set_defaults(func=cmd_merge)
