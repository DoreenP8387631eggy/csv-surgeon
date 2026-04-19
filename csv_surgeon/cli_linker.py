"""cli_linker.py — CLI commands for linking two CSV files by a shared key."""
import argparse
import csv
import sys
from csv_surgeon.linker import link_column, link_exists, link_count


def _read_rows(path: str):
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def cmd_link(args: argparse.Namespace) -> None:
    left = _read_rows(args.left)
    right = _read_rows(args.right)

    mode = args.mode
    if mode == "column":
        if not args.right_col:
            print("--right-col required for column mode", file=sys.stderr)
            sys.exit(1)
        rows = list(link_column(
            iter(left), iter(right),
            args.left_key, args.right_key,
            args.output_col, args.right_col,
            default=args.default,
            separator=args.separator,
        ))
    elif mode == "exists":
        rows = list(link_exists(
            iter(left), iter(right),
            args.left_key, args.right_key,
            output_col=args.output_col,
        ))
    elif mode == "count":
        rows = list(link_count(
            iter(left), iter(right),
            args.left_key, args.right_key,
            output_col=args.output_col,
        ))
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
        sys.exit(1)

    if not rows:
        return

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    writer = csv.DictWriter(out, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    if args.output:
        out.close()


def register(subparsers) -> None:
    p = subparsers.add_parser("link", help="Cross-reference two CSV files by key")
    p.add_argument("left", help="Primary CSV file")
    p.add_argument("right", help="Lookup CSV file")
    p.add_argument("--left-key", required=True, dest="left_key")
    p.add_argument("--right-key", required=True, dest="right_key")
    p.add_argument("--mode", choices=["column", "exists", "count"], default="exists")
    p.add_argument("--right-col", dest="right_col", default="")
    p.add_argument("--output-col", dest="output_col", default="linked")
    p.add_argument("--default", default="")
    p.add_argument("--separator", default="|")
    p.add_argument("--output", default="")
    p.set_defaults(func=cmd_link)
