"""CLI sub-commands for row scoring."""
import argparse
import csv
import sys
from csv_surgeon.scorer import score_rows, threshold_filter, rank_rows


def _parse_rule(spec: str):
    """Parse 'column:weight' into (column, lambda)."""
    parts = spec.split(":")
    col = parts[0].strip()
    weight = float(parts[1]) if len(parts) > 1 else 1.0
    return col, lambda v, w=weight: float(v) * w


def cmd_score(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rules = dict(_parse_rule(s) for s in args.rule)
    rows = score_rows(reader, rules, output_column=args.score_column)
    if args.min_score is not None:
        rows = threshold_filter(rows, args.score_column, args.min_score)
    if args.rank:
        rows = rank_rows(rows, args.score_column, descending=not args.ascending)
    rows = list(rows)
    if not rows:
        return
    writer = csv.DictWriter(args.output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)


def register(subparsers) -> None:
    p = subparsers.add_parser("score", help="Score rows by weighted column values")
    p.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", "-o", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument(
        "--rule", action="append", default=[],
        metavar="COL:WEIGHT",
        help="Scoring rule as column:weight (repeatable)",
    )
    p.add_argument("--score-column", default="__score__", metavar="COL")
    p.add_argument("--min-score", type=float, default=None, metavar="N")
    p.add_argument("--rank", action="store_true", help="Add rank column")
    p.add_argument("--ascending", action="store_true")
    p.set_defaults(func=cmd_score)
