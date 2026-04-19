"""CLI command for binning numeric columns."""
import argparse
import sys
from csv_surgeon.binner import bin_equal_width, bin_custom, bin_labels
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter


def cmd_bin(args: argparse.Namespace) -> None:
    reader = StreamingCSVReader(args.input)
    rows = reader.iter_rows()

    if args.mode == "equal":
        if args.min is None or args.max is None or args.n is None:
            print("equal mode requires --min, --max, --n", file=sys.stderr)
            sys.exit(1)
        result = bin_equal_width(
            rows,
            column=args.column,
            n_bins=args.n,
            min_val=args.min,
            max_val=args.max,
            out_col=args.out_col,
        )
    elif args.mode == "custom":
        if not args.edges:
            print("custom mode requires --edges", file=sys.stderr)
            sys.exit(1)
        edges = [float(e) for e in args.edges.split(",")]
        labels = args.labels.split(",") if args.labels else None
        result = bin_custom(
            rows,
            column=args.column,
            edges=edges,
            labels=labels,
            out_col=args.out_col,
        )
    else:
        print(f"Unknown mode: {args.mode}", file=sys.stderr)
        sys.exit(1)

    writer = StreamingCSVWriter(args.output)
    writer.write_rows(result)


def register(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser("bin", help="Bin a numeric column into labeled ranges")
    p.add_argument("input", help="Input CSV file")
    p.add_argument("output", help="Output CSV file")
    p.add_argument("--column", required=True, help="Column to bin")
    p.add_argument("--mode", choices=["equal", "custom"], default="equal")
    p.add_argument("--n", type=int, help="Number of equal-width bins")
    p.add_argument("--min", type=float, dest="min", help="Min value for equal-width")
    p.add_argument("--max", type=float, dest="max", help="Max value for equal-width")
    p.add_argument("--edges", help="Comma-separated bin edges for custom mode")
    p.add_argument("--labels", help="Comma-separated labels for custom mode")
    p.add_argument("--out-col", default="bin", help="Output column name")
    p.set_defaults(func=cmd_bin)
