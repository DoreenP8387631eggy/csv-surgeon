"""stacker.py — transpose rows into a key/value stacked format and back."""
from typing import Iterator, List, Dict


def stack_rows(
    rows: Iterator[Dict[str, str]],
    id_column: str,
    var_name: str = "variable",
    value_name: str = "value",
) -> Iterator[Dict[str, str]]:
    """Unpivot every non-id column into separate key/value rows.

    Each input row produces (number_of_columns - 1) output rows, one per
    non-id field.  The original column name is placed in *var_name* and
    the cell value in *value_name*.

    Args:
        rows:        Iterable of row dicts.
        id_column:   Column whose value is carried forward as the row
                     identifier.
        var_name:    Name for the new 'variable' column.
        value_name:  Name for the new 'value' column.

    Yields:
        Dicts with exactly three keys: id_column, var_name, value_name.
    """
    for row in rows:
        id_val = row.get(id_column, "")
        for col, val in row.items():
            if col == id_column:
                continue
            yield {id_column: id_val, var_name: col, value_name: val}


def unstack_rows(
    rows: Iterator[Dict[str, str]],
    id_column: str,
    var_column: str = "variable",
    value_column: str = "value",
    fill_value: str = "",
) -> Iterator[Dict[str, str]]:
    """Re-pivot stacked key/value rows back into wide format.

    All rows sharing the same *id_column* value are collapsed into a
    single output row whose extra columns come from *var_column* values.

    Args:
        rows:         Iterable of stacked row dicts.
        id_column:    Column that identifies the original row.
        var_column:   Column that holds the original column name.
        value_column: Column that holds the original cell value.
        fill_value:   Value used when a variable is absent for an id.

    Yields:
        Wide-format row dicts, one per unique id_column value.
    """
    # Buffer all rows so we can collect every variable name.
    buffered: List[Dict[str, str]] = list(rows)

    # Preserve insertion order for ids and variables.
    id_order: List[str] = []
    var_order: List[str] = []
    seen_ids: set = set()
    seen_vars: set = set()

    for row in buffered:
        id_val = row.get(id_column, "")
        var_val = row.get(var_column, "")
        if id_val not in seen_ids:
            id_order.append(id_val)
            seen_ids.add(id_val)
        if var_val not in seen_vars:
            var_order.append(var_val)
            seen_vars.add(var_val)

    # Build a lookup: {id_val: {var_val: value}}
    lookup: Dict[str, Dict[str, str]] = {id_val: {} for id_val in id_order}
    for row in buffered:
        lookup[row.get(id_column, "")][row.get(var_column, "")] = row.get(
            value_column, ""
        )

    for id_val in id_order:
        out: Dict[str, str] = {id_column: id_val}
        for var_val in var_order:
            out[var_val] = lookup[id_val].get(var_val, fill_value)
        yield out
