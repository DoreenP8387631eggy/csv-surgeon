"""CLI subcommand: fuzzy-dedup — remove near-duplicate rows."""
from __future__ import annotations
import argparse
import csv
import sys

from csv_surgeon.deduplicator_fuzzy import fuzzy_deduplicate, fuzzy_deduplicate_sorted


def cmd_fuzzy_dedup(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    if not reader.fieldnames:
        print("error: empty or missing CSV headers", file=sys.stderr)
        sys.exit(1)

    columns: list[str] = (
        [c.strip() for c in args.columns.split(",")]
        if args.columns
        else list(reader.fieldnames)
    )

    dedup_fn = fuzzy_deduplicate_sorted if args.sorted else fuzzy_deduplicate
    rows = dedup_fn(reader, columns=columns, threshold=args.threshold)

    writer = csv.DictWriter(
        args.output,
        fieldnames=reader.fieldnames,
        lineterminator="\n",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow(row)


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "fuzzy-dedup",
        help="Remove near-duplicate rows using fuzzy similarity.",
    )
    p.add_argument(
        "input",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input CSV file (default: stdin).",
    )
    p.add_argument(
        "-o", "--output",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Output CSV file (default: stdout).",
    )
    p.add_argument(
        "--columns",
        default=None,
        help="Comma-separated columns to compare (default: all columns).",
    )
    p.add_argument(
        "--threshold",
        type=float,
        default=0.85,
        help="Similarity threshold 0–1; rows at or above this are dropped (default: 0.85).",
    )
    p.add_argument(
        "--sorted",
        action="store_true",
        help="Assume input is sorted; only compare adjacent rows (faster).",
    )
    p.set_defaults(func=cmd_fuzzy_dedup)
