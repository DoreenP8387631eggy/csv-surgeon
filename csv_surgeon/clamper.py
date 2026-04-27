"""Column value length clamping — truncate or enforce minimum string length."""
from typing import Iterator, Optional


def _transform(rows: Iterator[dict], col: str, fn) -> Iterator[dict]:
    for row in rows:
        if col not in row:
            yield row
            continue
        out = dict(row)
        out[col] = fn(row[col])
        yield out


def clamp_length_min(
    rows: Iterator[dict],
    col: str,
    min_len: int,
    pad_char: str = " ",
    pad_right: bool = True,
) -> Iterator[dict]:
    """Pad values shorter than *min_len* with *pad_char*."""
    def fn(v: str) -> str:
        if len(v) >= min_len:
            return v
        padding = pad_char * (min_len - len(v))
        return v + padding if pad_right else padding + v

    return _transform(rows, col, fn)


def clamp_length_max(
    rows: Iterator[dict],
    col: str,
    max_len: int,
    suffix: str = "",
) -> Iterator[dict]:
    """Truncate values longer than *max_len*, optionally appending *suffix*."""
    def fn(v: str) -> str:
        if len(v) <= max_len:
            return v
        cut = max_len - len(suffix)
        return v[:cut] + suffix if cut >= 0 else suffix[:max_len]

    return _transform(rows, col, fn)


def clamp_length(
    rows: Iterator[dict],
    col: str,
    min_len: Optional[int] = None,
    max_len: Optional[int] = None,
    pad_char: str = " ",
    pad_right: bool = True,
    suffix: str = "",
) -> Iterator[dict]:
    """Apply both min and max length clamping in a single pass."""
    def fn(v: str) -> str:
        result = v
        if min_len is not None and len(result) < min_len:
            padding = pad_char * (min_len - len(result))
            result = result + padding if pad_right else padding + result
        if max_len is not None and len(result) > max_len:
            cut = max_len - len(suffix)
            result = result[:cut] + suffix if cut >= 0 else suffix[:max_len]
        return result

    return _transform(rows, col, fn)
