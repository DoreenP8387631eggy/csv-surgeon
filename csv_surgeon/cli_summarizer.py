"""CLI command for summarizing CSV column statistics."""
import argparse
import csv
import sys
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.summarizer import summarize_rows, summary_to_rows
from csv_surgeon.writer import StreamingCSVWriter


def cmd_summarize(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    columns = args.columns.split(",") if args.columns else None
    stats = summarize_rows(reader.iter_rows(), columns=columns)
    rows = list(summary_to_rows(stats))

    if not rows:
        print("No data to summarize.", file=sys.stderr)
        return

    output_headers = list(rows[0].keys())
    writer = StreamingCSVWriter(args.output, headers=output_headers)
    writer.write_rows(iter(rows))


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "summarize",
        help="Print summary statistics for each column.",
    )
    p.add_argument("input", help="Input CSV file path")
    p.add_argument("output", help="Output CSV file path")
    p.add_argument(
        "--columns",
        default=None,
        help="Comma-separated list of columns to summarize (default: all)",
    )
    p.set_defaults(func=cmd_summarize)
