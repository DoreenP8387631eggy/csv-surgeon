from typing import Callable, Dict, List, Optional


TransformFn = Callable[[Dict[str, str]], Optional[Dict[str, str]]]


def rename_column(old_name: str, new_name: str) -> TransformFn:
    """Rename a column in each row dict."""
    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        if old_name in row:
            row[new_name] = row.pop(old_name)
        return row
    return _transform


def add_column(name: str, value_fn: Callable[[Dict[str, str]], str]) -> TransformFn:
    """Add a computed column to each row."""
    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        row[name] = value_fn(row)
        return row
    return _transform


def drop_column(name: str) -> TransformFn:
    """Remove a column from each row dict."""
    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        row.pop(name, None)
        return row
    return _transform


def map_column(name: str, fn: Callable[[str], str]) -> TransformFn:
    """Apply a function to the value of a single column."""
    def _transform(row: Dict[str, str]) -> Dict[str, str]:
        if name in row:
            row[name] = fn(row[name])
        return row
    return _transform


class TransformPipeline:
    """Applies a sequence of row-level transformations."""

    def __init__(self):
        self._transforms: List[TransformFn] = []

    def add_transform(self, fn: TransformFn) -> "TransformPipeline":
        self._transforms.append(fn)
        return self

    def clear_transforms(self):
        self._transforms.clear()

    def apply(self, row: Dict[str, str]) -> Optional[Dict[str, str]]:
        for fn in self._transforms:
            if row is None:
                return None
            row = fn(row)
        return row

    def apply_all(self, rows):
        for row in rows:
            result = self.apply(dict(row))
            if result is not None:
                yield result
