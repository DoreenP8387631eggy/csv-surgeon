"""CLI command for fuzzy joining two CSV files on a shared key column."""

import argparse
import csv
import io
import sys
from csv_surgeon.joiner_fuzzy import fuzzy_inner_join, fuzzy_left_join


def _read_rows(path: str) -> list[dict]:
    """Read all rows from a CSV file into a list of dicts."""
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def cmd_fuzzy_join(args: argparse.Namespace) -> None:
    """Perform a fuzzy join between two CSV files and write the result to stdout.

    Parameters
    ----------
    args:
        Parsed CLI arguments containing:
        - left: path to the left CSV file
        - right: path to the right CSV file
        - left_key: column name in the left file to join on
        - right_key: column name in the right file to join on (defaults to left_key)
        - threshold: minimum similarity score to consider a match (0.0–1.0)
        - join_type: "inner" or "left"
        - output_score: if set, include the similarity score column in output
    """
    left_rows = _read_rows(args.left)
    right_rows = _read_rows(args.right)

    if not left_rows:
        sys.stderr.write("Left file is empty or has no data rows.\n")
        sys.exit(1)

    if not right_rows:
        sys.stderr.write("Right file is empty or has no data rows.\n")
        sys.exit(1)

    right_key = args.right_key or args.left_key
    threshold = args.threshold

    join_fn = fuzzy_inner_join if args.join_type == "inner" else fuzzy_left_join

    try:
        result = list(
            join_fn(
                left_rows,
                right_rows,
                left_key=args.left_key,
                right_key=right_key,
                threshold=threshold,
            )
        )
    except KeyError as exc:
        sys.stderr.write(f"Key column not found: {exc}\n")
        sys.exit(1)

    if not result:
        sys.stderr.write("No matching rows found.\n")
        sys.exit(0)

    # Optionally remove the internal similarity score column from output
    if not args.output_score:
        for row in result:
            row.pop("_similarity", None)

    fieldnames = list(result[0].keys())
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=fieldnames,
        lineterminator="\n",
        extrasaction="ignore",
    )
    writer.writeheader()
    writer.writerows(result)


def register(subparsers: argparse._SubParsersAction) -> None:
    """Register the fuzzy-join subcommand with the given subparser group."""
    parser = subparsers.add_parser(
        "fuzzy-join",
        help="Join two CSV files using fuzzy string matching on a key column.",
    )
    parser.add_argument("left", help="Path to the left CSV file.")
    parser.add_argument("right", help="Path to the right CSV file.")
    parser.add_argument(
        "--left-key",
        dest="left_key",
        required=True,
        help="Column in the left file to join on.",
    )
    parser.add_argument(
        "--right-key",
        dest="right_key",
        default=None,
        help="Column in the right file to join on (defaults to --left-key).",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Minimum similarity score (0.0–1.0) to treat two values as a match. Default: 0.8.",
    )
    parser.add_argument(
        "--join-type",
        dest="join_type",
        choices=["inner", "left"],
        default="inner",
        help="Type of join to perform: 'inner' (default) or 'left'.",
    )
    parser.add_argument(
        "--output-score",
        dest="output_score",
        action="store_true",
        default=False,
        help="Include the _similarity score column in the output.",
    )
    parser.set_defaults(func=cmd_fuzzy_join)
