import argparse
import sys
import csv
from csv_surgeon.extractor import extract_pattern, extract_all_patterns, extract_named_groups, extract_between


def cmd_extract(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = list(reader)

    if args.mode == "pattern":
        transform = extract_pattern(
            args.column, args.pattern,
            output_col=args.output_col,
            group=args.group,
            default=args.default,
        )
    elif args.mode == "all":
        transform = extract_all_patterns(
            args.column, args.pattern,
            output_col=args.output_col,
            separator=args.separator,
            default=args.default,
        )
    elif args.mode == "named":
        transform = extract_named_groups(args.column, args.pattern, default=args.default)
    elif args.mode == "between":
        transform = extract_between(
            args.column, args.start, args.end,
            output_col=args.output_col,
            default=args.default,
        )
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    transformed = [transform(r) for r in rows]
    if not transformed:
        return

    writer = csv.DictWriter(args.output, fieldnames=list(transformed[0].keys()))
    writer.writeheader()
    writer.writerows(transformed)


def register(subparsers) -> None:
    p = subparsers.add_parser("extract", help="Extract regex matches into new columns")
    p.add_argument("--column", required=True)
    p.add_argument("--pattern", default="")
    p.add_argument("--mode", choices=["pattern", "all", "named", "between"], default="pattern")
    p.add_argument("--output-col", dest="output_col", default=None)
    p.add_argument("--group", type=int, default=0)
    p.add_argument("--separator", default="|")
    p.add_argument("--default", default="")
    p.add_argument("--start", default="")
    p.add_argument("--end", default="")
    p.add_argument("input", type=argparse.FileType("r"), default=sys.stdin, nargs="?")
    p.add_argument("output", type=argparse.FileType("w"), default=sys.stdout, nargs="?")
    p.set_defaults(func=cmd_extract)
