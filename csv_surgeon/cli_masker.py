"""CLI sub-command for masking sensitive columns."""

import argparse
import csv
import sys
from csv_surgeon.masker import mask_column, redact_column, mask_pattern
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def cmd_mask(args: argparse.Namespace) -> None:
    """Apply masking transforms to one or more columns and write output."""

    if not any([args.mask, args.redact, args.mask_pattern]):
        print("error: at least one of --mask, --redact, or --mask-pattern is required.",
              file=sys.stderr)
        sys.exit(1)

    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()

    # Build transform chain
    transforms = []

    for col in (args.mask or []):
        transforms.append(mask_column(col, keep_last=args.keep_last))

    for col in (args.redact or []):
        transforms.append(redact_column(col, replacement=args.replacement))

    for spec in (args.mask_pattern or []):
        if ":" not in spec:
            print(f"error: --mask-pattern must be in 'column:pattern' format, got: {spec}",
                  file=sys.stderr)
            sys.exit(1)
        col, pattern = spec.split(":", 1)
        transforms.append(mask_pattern(col, pattern))

    for transform in transforms:
        rows = transform(rows)

    writer = StreamingCSVWriter(args.output)
    writer.write_rows(reader.headers, rows)


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    parser = subparsers.add_parser("mask", help="Mask or redact sensitive column values.")
    parser.add_argument("input", help="Input CSV file path.")
    parser.add_argument("output", help="Output CSV file path.")
    parser.add_argument("--mask", metavar="COLUMN", nargs="+",
                        help="Columns to mask with asterisks.")
    parser.add_argument("--keep-last", type=int, default=0, metavar="N",
                        help="Number of trailing characters to keep visible when masking.")
    parser.add_argument("--redact", metavar="COLUMN", nargs="+",
                        help="Columns to fully redact.")
    parser.add_argument("--replacement", default="[REDACTED]",
                        help="Replacement string for redacted columns (default: [REDACTED]).")
    parser.add_argument("--mask-pattern", metavar="COLUMN:PATTERN", nargs="+",
                        help="Mask regex pattern matches within a column (format: column:pattern).")
    parser.set_defaults(func=cmd_mask)
