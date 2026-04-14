"""Streaming pipeline that applies filters to a CSV reader."""

from typing import Iterator, List, Optional, Dict, Any

from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.filters import RowFilter


class FilterPipeline:
    """Applies a chain of row filters to a StreamingCSVReader.

    Rows are processed one at a time without loading the full file
    into memory.
    """

    def __init__(self, reader: StreamingCSVReader) -> None:
        self._reader = reader
        self._filters: List[RowFilter] = []

    def add_filter(self, f: RowFilter) -> "FilterPipeline":
        """Add a filter to the pipeline. Returns self for chaining."""
        self._filters.append(f)
        return self

    def clear_filters(self) -> "FilterPipeline":
        """Remove all filters from the pipeline."""
        self._filters.clear()
        return self

    def _row_passes(self, row: Dict[str, Any]) -> bool:
        """Return True if the row satisfies all filters."""
        return all(f(row) for f in self._filters)

    def iter_filtered(self) -> Iterator[Dict[str, Any]]:
        """Yield rows that pass all filters in the pipeline."""
        for row in self._reader.iter_rows():
            if self._row_passes(row):
                yield row

    def count(self) -> int:
        """Count rows that pass all filters without storing them."""
        total = 0
        for _ in self.iter_filtered():
            total += 1
        return total

    @property
    def headers(self) -> Optional[List[str]]:
        """Expose the underlying reader's headers."""
        return self._reader.headers
