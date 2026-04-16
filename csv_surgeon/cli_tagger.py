"""CLI command for tagging rows with labels."""

import argparse
import csv
import sys

from csv_surgeon.tagger import tag_column, tag_multi, tag_equals, tag_contains, tag_numeric_range


def _parse_rule(spec: str):
    """Parse a rule spec: equals:col:val:tag | contains:col:val:tag | range:col:low:high:tag"""
    parts = spec.split(":")
    kind = parts[0].lower()
    if kind == "equals" and len(parts) == 4:
        return tag_equals(parts[1], parts[2], parts[3])
    if kind == "contains" and len(parts) == 4:
        return tag_contains(parts[1], parts[2], parts[3])
    if kind == "range" and len(parts) == 5:
        return tag_numeric_range(parts[1], float(parts[2]), float(parts[3]), parts[4])
    raise ValueError(f"Invalid rule spec: {spec!r}")


def cmd_tag(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rules = [_parse_rule(s) for s in (args.rule or [])]

    if args.multi:
        rows = tag_multi(reader, args.tag_column, rules, separator=args.separator)
    else:
        rows = tag_column(reader, args.tag_column, rules, default=args.default)

    first = next(iter([None]), None)  # peek handled by writer
    writer = None
    for row in rows:
        if writer is None:
            writer = csv.DictWriter(args.output, fieldnames=list(row.keys()))
            writer.writeheader()
        writer.writerow(row)


def register(subparsers) -> None:
    p = subparsers.add_parser("tag", help="Tag rows with labels based on rules")
    p.add_argument("input", nargs="?", type=argparse.FileType("r"), default=sys.stdin)
    p.add_argument("--output", "-o", type=argparse.FileType("w"), default=sys.stdout)
    p.add_argument("--tag-column", default="tag", help="Name of the output tag column")
    p.add_argument(
        "--rule", action="append",
        help="Rule spec: equals:col:val:tag | contains:col:val:tag | range:col:low:high:tag",
    )
    p.add_argument("--multi", action="store_true", help="Apply all matching rules (not just first)")
    p.add_argument("--separator", default="|", help="Separator for multi-tag mode")
    p.add_argument("--default", default="", help="Default tag when no rule matches")
    p.set_defaults(func=cmd_tag)
