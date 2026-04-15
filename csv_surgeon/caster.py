"""Column type casting utilities for CSV rows."""

from typing import Iterator, Dict, Any


def cast_column(column: str, cast_type: str):
    """Return a transform that casts a column to the given type string.

    Supported types: 'int', 'float', 'bool', 'str'.
    On failure the original value is preserved.
    """
    _casters = {
        "int": _to_int,
        "float": _to_float,
        "bool": _to_bool,
        "str": str,
    }
    if cast_type not in _casters:
        raise ValueError(f"Unsupported cast type: {cast_type!r}. Choose from {list(_casters)}.")

    caster = _casters[cast_type]

    def _transform(rows: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        for row in rows:
            if column not in row:
                yield row
                continue
            try:
                row = dict(row)
                row[column] = caster(row[column])
            except (ValueError, TypeError):
                pass
            yield row

    return _transform


def cast_columns(mapping: Dict[str, str]):
    """Return a transform that casts multiple columns according to a mapping
    of {column_name: type_string}.
    """
    transforms = [cast_column(col, typ) for col, typ in mapping.items()]

    def _transform(rows: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        stream = rows
        for t in transforms:
            stream = t(stream)
        yield from stream

    return _transform


# --- helpers ---

def _to_int(value: Any) -> int:
    return int(float(str(value).strip()))


def _to_float(value: Any) -> float:
    return float(str(value).strip())


def _to_bool(value: Any) -> bool:
    s = str(value).strip().lower()
    if s in ("1", "true", "yes", "y"):
        return True
    if s in ("0", "false", "no", "n", ""):
        return False
    raise ValueError(f"Cannot cast {value!r} to bool")
