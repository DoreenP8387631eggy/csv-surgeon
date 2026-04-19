"""CLI command for sequencer module."""
import argparse
import csv
import sys
from csv_surgeon.sequencer import sequence_column, alpha_sequence_column, cycle_column, repeat_column


def cmd_sequence(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    if args.mode == "int":
        result = sequence_column(rows, args.col, start=args.start, step=args.step, overwrite=args.overwrite)
    elif args.mode == "alpha":
        result = alpha_sequence_column(rows, args.col, prefix=args.prefix, start=args.start, step=args.step, pad=args.pad)
    elif args.mode == "cycle":
        result = cycle_column(rows, args.col, args.values)
    elif args.mode == "repeat":
        result = repeat_column(rows, args.col, args.value, overwrite=args.overwrite)
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    first = next(result, None)
    if first is None:
        return
    writer = csv.DictWriter(args.output, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(result)


def register(subparsers) -> None:
    p = subparsers.add_parser("sequence", help="Add sequential/patterned column values")
    p.add_argument("input", type=argparse.FileType("r"), default="-")
    p.add_argument("--output", type=argparse.FileType("w"), default="-")
    p.add_argument("--col", required=True, help="Output column name")
    p.add_argument("--mode", choices=["int", "alpha", "cycle", "repeat"], default="int")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--step", type=int, default=1)
    p.add_argument("--prefix", default="")
    p.add_argument("--pad", type=int, default=0)
    p.add_argument("--values", nargs="+", default=[])
    p.add_argument("--value", default="")
    p.add_argument("--overwrite", action="store_true")
    p.set_defaults(func=cmd_sequence)
