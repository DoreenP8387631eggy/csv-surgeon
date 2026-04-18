"""CLI command for diffing two CSV files."""
import argparse
import csv
import sys
from csv_surgeon.differ import unified_diff, only_changed, diff_summary


def cmd_diff(args: argparse.Namespace) -> None:
    def _read(path):
        with open(path, newline="") as f:
            return list(csv.DictReader(f))

    before_rows = _read(args.before)
    after_rows = _read(args.after)

    track = args.track.split(",") if args.track else None
    diff = unified_diff(iter(before_rows), iter(after_rows), args.key, track)

    if args.summary:
        # consume and print summary only
        counts = diff_summary(diff)
        for status, count in counts.items():
            print(f"{status}: {count}")
        return

    if args.changed_only:
        diff = only_changed(diff)

    rows = list(diff)
    if not rows:
        return

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    if args.output:
        out.close()


def register(subparsers) -> None:
    p = subparsers.add_parser("diff", help="Diff two CSV files row by row")
    p.add_argument("before", help="Path to the original CSV file")
    p.add_argument("after", help="Path to the new CSV file")
    p.add_argument("--key", required=True, help="Column to use as the row key")
    p.add_argument("--track", default=None, help="Comma-separated columns to compare (default: all)")
    p.add_argument("--changed-only", action="store_true", help="Only output changed/added/removed rows")
    p.add_argument("--summary", action="store_true", help="Print a summary count instead of rows")
    p.add_argument("--output", default=None, help="Output file path (default: stdout)")
    p.set_defaults(func=cmd_diff)
