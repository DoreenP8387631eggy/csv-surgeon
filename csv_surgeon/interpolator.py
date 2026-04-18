"""Column interpolation: fill missing/empty values using surrounding rows."""
from typing import Iterator, Optional


def _to_float(v: str) -> Optional[float]:
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def interpolate_column(
    column: str,
    method: str = "linear",
    fill_value: str = "",
) -> callable:
    """Return a transform that fills empty values by linear interpolation.

    Buffers the full stream so it can look ahead. For streaming-friendly
    forward-fill / back-fill use ffill_column / bfill_column instead.
    """
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        buffered = list(rows)
        if not buffered:
            return

        if method == "linear":
            # collect (index, value) pairs for known numeric values
            known: list[tuple[int, float]] = []
            for i, row in enumerate(buffered):
                v = _to_float(row.get(column, ""))
                if v is not None and row.get(column, "").strip() != "":
                    known.append((i, v))

            for i, row in enumerate(buffered):
                row = dict(row)
                if row.get(column, "").strip() == "":
                    left = next(((idx, val) for idx, val in reversed(known) if idx < i), None)
                    right = next(((idx, val) for idx, val in known if idx > i), None)
                    if left and right:
                        li, lv = left
                        ri, rv = right
                        ratio = (i - li) / (ri - li)
                        row[column] = str(round(lv + ratio * (rv - lv), 10))
                    elif left:
                        row[column] = str(left[1])
                    elif right:
                        row[column] = str(right[1])
                    else:
                        row[column] = fill_value
                yield row
        else:
            yield from buffered

    return _transform


def ffill_column(column: str, fill_value: str = "") -> callable:
    """Forward-fill: propagate last seen non-empty value downward."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        last: Optional[str] = None
        for row in rows:
            row = dict(row)
            val = row.get(column, "").strip()
            if val:
                last = val
                yield row
            else:
                row[column] = last if last is not None else fill_value
                yield row
    return _transform


def bfill_column(column: str, fill_value: str = "") -> callable:
    """Back-fill: propagate next non-empty value upward."""
    def _transform(rows: Iterator[dict]) -> Iterator[dict]:
        buffered = list(rows)
        result = [dict(r) for r in buffered]
        last: Optional[str] = None
        for i in range(len(result) - 1, -1, -1):
            val = result[i].get(column, "").strip()
            if val:
                last = val
            elif last is not None:
                result[i][column] = last
            else:
                result[i][column] = fill_value
        yield from result
    return _transform
