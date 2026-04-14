import csv
import io
from typing import Iterator, List, Optional


class StreamingCSVWriter:
    """
    Writes CSV rows to a file or stream without buffering all rows in memory.
    Supports writing headers and rows incrementally.
    """

    def __init__(
        self,
        output_path: Optional[str] = None,
        stream: Optional[io.IOBase] = None,
        delimiter: str = ",",
        quotechar: str = '"',
        lineterminator: str = "\n",
    ):
        if output_path is None and stream is None:
            raise ValueError("Either output_path or stream must be provided.")
        self._output_path = output_path
        self._stream = stream
        self._delimiter = delimiter
        self._quotechar = quotechar
        self._lineterminator = lineterminator
        self._rows_written = 0

    def write_rows(
        self,
        rows: Iterator[dict],
        headers: List[str],
        include_header: bool = True,
    ) -> int:
        """
        Write rows (as dicts) to the output. Returns the number of data rows written.
        """
        writer_kwargs = dict(
            delimiter=self._delimiter,
            quotechar=self._quotechar,
            lineterminator=self._lineterminator,
        )

        def _write(f):
            writer = csv.DictWriter(f, fieldnames=headers, **writer_kwargs)
            if include_header:
                writer.writeheader()
            count = 0
            for row in rows:
                writer.writerow({k: row.get(k, "") for k in headers})
                count += 1
            return count

        if self._output_path:
            with open(self._output_path, "w", newline="", encoding="utf-8") as f:
                self._rows_written = _write(f)
        else:
            self._rows_written = _write(self._stream)

        return self._rows_written

    @property
    def rows_written(self) -> int:
        return self._rows_written
