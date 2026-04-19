"""CLI command for scaling numeric columns."""
import argparse
import csv
import sys
from csv_surgeon.scaler import minmax_scale, zscore_scale, robust_scale


def cmd_scale(args: argparse.Namespace) -> None:
    reader = csv.DictReader(args.input)
    rows = list(reader)

    method = args.method
    out_col = args.output_column or None

    if method == "minmax":
        lo, hi = args.range
        result = minmax_scale(iter(rows), column=args.column,
                              out_col=out_col, feature_range=(lo, hi))
    elif method == "zscore":
        result = zscore_scale(iter(rows), column=args.column, out_col=out_col)
    elif method == "robust":
        result = robust_scale(iter(rows), column=args.column, out_col=out_col)
    else:
        print(f"Unknown method: {method}", file=sys.stderr)
        sys.exit(1)

    result = list(result)
    if not result:
        return

    writer = csv.DictWriter(args.output, fieldnames=list(result[0].keys()))
    writer.writeheader()
    writer.writerows(result)


def register(subparsers) -> None:
    p = subparsers.add_parser("scale", help="Scale a numeric column")
    p.add_argument("input", type=argparse.FileType("r"), default="-", nargs="?")
    p.add_argument("--column", required=True, help="Column to scale")
    p.add_argument("--method", choices=["minmax", "zscore", "robust"], default="minmax")
    p.add_argument("--output-column", default="", help="Output column name (default: in-place)")
    p.add_argument("--range", nargs=2, type=float, default=[0.0, 1.0],
                   metavar=("MIN", "MAX"), help="Feature range for minmax (default: 0 1)")
    p.add_argument("--output", "-o", type=argparse.FileType("w"), default=sys.stdout)
    p.set_defaults(func=cmd_scale)
