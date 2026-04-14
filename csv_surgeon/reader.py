"""Streaming CSV reader that processes rows without loading the full file into memory."""

import csv
from typing import Iterator, Optional


class StreamingCSVReader:
    """Reads a CSV file row by row using a generator to minimize memory usage."""

    def __init__(
        self,
        filepath: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        skip_blank_lines: bool = True,
    ) -> None:
        self.filepath = filepath
        self.delimiter = delimiter
        self.encoding = encoding
        self.skip_blank_lines = skip_blank_lines
        self._headers: Optional[list[str]] = None

    @property
    def headers(self) -> Optional[list[str]]:
        """Return cached headers if already read."""
        return self._headers

    def iter_rows(self) -> Iterator[dict[str, str]]:
        """Yield each data row as a dict keyed by column header."""
        with open(self.filepath, newline="", encoding=self.encoding) as fh:
            reader = csv.DictReader(fh, delimiter=self.delimiter)
            self._headers = list(reader.fieldnames or [])
            for row in reader:
                if self.skip_blank_lines and all(v.strip() == "" for v in row.values()):
                    continue
                yield dict(row)

    def iter_raw_rows(self) -> Iterator[list[str]]:
        """Yield each row as a plain list of strings (no header mapping)."""
        with open(self.filepath, newline="", encoding=self.encoding) as fh:
            reader = csv.reader(fh, delimiter=self.delimiter)
            for row in reader:
                if self.skip_blank_lines and all(cell.strip() == "" for cell in row):
                    continue
                yield row

    def peek_headers(self) -> list[str]:
        """Read only the header row without iterating the entire file."""
        with open(self.filepath, newline="", encoding=self.encoding) as fh:
            reader = csv.reader(fh, delimiter=self.delimiter)
            headers = next(reader, [])
        self._headers = headers
        return headers
