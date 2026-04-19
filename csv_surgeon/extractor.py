import re
from typing import Iterator, Dict, Optional


def extract_pattern(
    column: str,
    pattern: str,
    output_col: Optional[str] = None,
    group: int = 0,
    default: str = "",
) -> callable:
    """Extract a regex match (or group) from a column into a new column."""
    compiled = re.compile(pattern)
    out = output_col or f"{column}_extracted"

    def _transform(row: Dict) -> Dict:
        val = row.get(column, "")
        m = compiled.search(val)
        result = m.group(group) if m else default
        return {**row, out: result}

    return _transform


def extract_all_patterns(
    column: str,
    pattern: str,
    output_col: Optional[str] = None,
    separator: str = "|",
    default: str = "",
) -> callable:
    """Extract all non-overlapping matches and join them with separator."""
    compiled = re.compile(pattern)
    out = output_col or f"{column}_all"

    def _transform(row: Dict) -> Dict:
        val = row.get(column, "")
        matches = compiled.findall(val)
        result = separator.join(matches) if matches else default
        return {**row, out: result}

    return _transform


def extract_named_groups(
    column: str,
    pattern: str,
    default: str = "",
) -> callable:
    """Extract named groups from a regex pattern into separate columns."""
    compiled = re.compile(pattern)
    group_names = list(compiled.groupindex.keys())

    def _transform(row: Dict) -> Dict:
        val = row.get(column, "")
        m = compiled.search(val)
        new_cols = {name: (m.group(name) if m else default) for name in group_names}
        return {**row, **new_cols}

    return _transform


def extract_between(
    column: str,
    start: str,
    end: str,
    output_col: Optional[str] = None,
    default: str = "",
) -> callable:
    """Extract text between two literal delimiters."""
    pattern = re.compile(re.escape(start) + r"(.*?)" + re.escape(end), re.DOTALL)
    out = output_col or f"{column}_between"

    def _transform(row: Dict) -> Dict:
        val = row.get(column, "")
        m = pattern.search(val)
        result = m.group(1) if m else default
        return {**row, out: result}

    return _transform
