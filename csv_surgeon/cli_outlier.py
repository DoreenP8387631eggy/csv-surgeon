"""CLI command for outlier detection."""
import argparse
import csv
import sys
from csv_surgeon.outlier import flag_zscore, flag_iqr


def cmd_outlier(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = iter(reader)

    if args.method == "zscore":
        result = flag_zscore(rows, args.column,
                             threshold=args.threshold,
                             output_col=args.output_col)
    elif args.method == "iqr":
        result = flag_iqr(rows, args.column,
                          multiplier=args.multiplier,
                          output_col=args.output_col)
    else:
        print(f"Unknown method: {args.method}", file=sys.stderr)
        sys.exit(1)

    first = next(result, None)
    if first is None:
        return

    writer = csv.DictWriter(args.output, fieldnames=list(first.keys()))
    writer.writeheader()
    writer.writerow(first)
    writer.writerows(result)


def register(subparsers) -> None:
    p = subparsers.add_parser("outlier", help="Flag outlier rows in a numeric column")
    p.add_argument("input", type=argparse.FileType("r"), help="Input CSV file")
    p.add_argument("output", type=argparse.FileType("w"), help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to analyse")
    p.add_argument("--method", choices=["zscore", "iqr"], default="zscore")
    p.add_argument("--threshold", type=float, default=3.0,
                   help="Z-score threshold (zscore method)")
    p.add_argument("--multiplier", type=float, default=1.5,
                   help="IQR multiplier (iqr method)")
    p.add_argument("--output-col", dest="output_col", default="is_outlier")
    p.set_defaults(func=cmd_outlier)
