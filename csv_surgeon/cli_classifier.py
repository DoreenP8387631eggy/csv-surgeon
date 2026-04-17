"""CLI command for classifying rows."""
import argparse
import csv
import sys

from csv_surgeon.classifier import build_rule, classify_rows


def _parse_rule(spec: str) -> tuple[str, str, str, str]:
    """Parse a rule spec: 'label:column:operator:value'."""
    parts = spec.split(":", 3)
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            f"Rule must be 'label:column:operator:value', got: {spec!r}"
        )
    return tuple(parts)  # type: ignore[return-value]


def cmd_classify(args: argparse.Namespace) -> None:
    rules = [build_rule(*_parse_rule(r)) for r in args.rule]
    if not rules:
        print("Error: at least one --rule is required.", file=sys.stderr)
        sys.exit(1)

    with open(args.input, newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)

    classified = classify_rows(
        rows,
        rules,
        output_column=args.output_column,
        default=args.default,
    )

    out = open(args.output, "w", newline="") if args.output else sys.stdout
    try:
        writer = None
        for row in classified:
            if writer is None:
                writer = csv.DictWriter(out, fieldnames=list(row.keys()))
                writer.writeheader()
            writer.writerow(row)
    finally:
        if args.output:
            out.close()


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("classify", help="Classify rows by rule priority")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("--rule", action="append", default=[], metavar="LABEL:COL:OP:VALUE")
    p.add_argument("--output-column", default="class", help="Column name for class label")
    p.add_argument("--default", default="", help="Default label when no rule matches")
    p.add_argument("--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=cmd_classify)
