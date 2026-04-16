"""Column type inference for CSV rows."""

from typing import Iterator, Dict, Any


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except (ValueError, TypeError):
        return False


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _is_bool(value: str) -> bool:
    return value.strip().lower() in ("true", "false", "1", "0", "yes", "no")


def infer_column_types(rows: list[Dict[str, str]]) -> Dict[str, str]:
    """Infer the most specific type for each column across all rows.

    Returns a dict mapping column name -> inferred type string:
    one of 'int', 'float', 'bool', or 'str'.
    """
    if not rows:
        return {}

    columns = list(rows[0].keys())
    types: Dict[str, str] = {col: "int" for col in columns}

    for row in rows:
        for col in columns:
            value = row.get(col, "").strip()
            if value == "":
                continue
            current = types[col]
            if current == "int" and not _is_int(value):
                types[col] = "float"
                current = "float"
            if current == "float" and not _is_float(value):
                types[col] = "bool"
                current = "bool"
            if current == "bool" and not _is_bool(value):
                types[col] = "str"

    return types


def annotate_row(row: Dict[str, str], type_map: Dict[str, str]) -> Dict[str, Any]:
    """Cast a row's values to their inferred Python types."""
    result: Dict[str, Any] = {}
    for col, value in row.items():
        t = type_map.get(col, "str")
        stripped = value.strip()
        if stripped == "":
            result[col] = value
            continue
        try:
            if t == "int":
                result[col] = int(stripped)
            elif t == "float":
                result[col] = float(stripped)
            elif t == "bool":
                result[col] = stripped.lower() in ("true", "1", "yes")
            else:
                result[col] = value
        except (ValueError, TypeError):
            result[col] = value
    return result


def annotate_rows(
    rows: Iterator[Dict[str, str]], type_map: Dict[str, str]
) -> Iterator[Dict[str, Any]]:
    """Lazily annotate rows using a pre-computed type map."""
    for row in rows:
        yield annotate_row(row, type_map)
