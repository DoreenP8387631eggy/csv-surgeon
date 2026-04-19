"""cli_clipper.py – CLI subcommands for clamp/clip operations."""
import argparse
import csv
import sys

from csv_surgeon.clipper import clamp_column, clip_below, clip_above


def cmd_clip(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    if args.mode == "clamp":
        transformed = clamp_column(
            rows,
            column=args.column,
            min_value=float(args.min) if args.min is not None else None,
            max_value=float(args.max) if args.max is not None else None,
            output_column=args.output_column,
        )
    elif args.mode == "below":
        transformed = clip_below(
            rows,
            column=args.column,
            threshold=float(args.threshold),
            replacement=args.replacement,
            output_column=args.output_column,
        )
    elif args.mode == "above":
        transformed = clip_above(
            rows,
            column=args.column,
            threshold=float(args.threshold),
            replacement=args.replacement,
            output_column=args.output_column,
        )
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    first = next(transformed, None)
    if first is None:
        return
    writer = csv.DictWriter(args.output, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(transformed)


def register(subparsers) -> None:
    p = subparsers.add_parser("clip", help="Clamp or clip numeric column values")
    p.add_argument("--input", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("--column", required=True)
    p.add_argument("--mode", choices=["clamp", "below", "above"], default="clamp")
    p.add_argument("--min", default=None)
    p.add_argument("--max", default=None)
    p.add_argument("--threshold", default=None)
    p.add_argument("--replacement", default="")
    p.add_argument("--output-column", dest="output_column", default=None)
    p.set_defaults(func=cmd_clip)
