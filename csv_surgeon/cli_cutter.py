"""cli_cutter.py – CLI sub-command for the cutter module."""
from __future__ import annotations

import argparse
import csv
import sys

from csv_surgeon import cutter


def cmd_cut(args: argparse.Namespace) -> None:
    reader = csv.DictReader(sys.stdin)
    rows = iter(reader)

    if args.mode == "chars":
        end = args.end if args.end is not None else None
        result = cutter.cut_chars(rows, args.column, args.start, end, args.out_col)
    elif args.mode == "before":
        result = cutter.cut_before(rows, args.column, args.sep, args.out_col)
    elif args.mode == "after":
        result = cutter.cut_after(rows, args.column, args.sep, args.out_col)
    elif args.mode == "words":
        end = args.end if args.end is not None else None
        result = cutter.cut_words(rows, args.column, args.start, end,
                                  args.sep or " ", args.out_col)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    result_list = list(result)
    if not result_list:
        return

    fieldnames = list(result_list[0].keys())
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(result_list)


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("cut", help="Slice column values by position or separator")
    p.add_argument("column", help="Column to cut")
    p.add_argument("mode", choices=["chars", "before", "after", "words"],
                   help="Cutting mode")
    p.add_argument("--start", type=int, default=0,
                   help="Start index (chars/words mode)")
    p.add_argument("--end", type=int, default=None,
                   help="End index exclusive (chars/words mode)")
    p.add_argument("--sep", default=None,
                   help="Separator string (before/after/words mode)")
    p.add_argument("--out-col", dest="out_col", default=None,
                   help="Output column name (default: overwrite source column)")
    p.set_defaults(func=cmd_cut)
