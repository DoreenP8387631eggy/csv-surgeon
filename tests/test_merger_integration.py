"""Integration tests: merge_rows used with StreamingCSVReader and StreamingCSVWriter."""
import io
import pytest
from csv_surgeon.reader import StreamingCSVReader
from csv_surgeon.writer import StreamingCSVWriter
from csv_surgeon.merger import merge_rows


@pytest.fixture
def file_a(tmp_path):
    p = tmp_path / "a.csv"
    p.write_text("id,city\n1,London\n2,Paris\n")
    return str(p)


@pytest.fixture
def file_b(tmp_path):
    p = tmp_path / "b.csv"
    p.write_text("id,city\n3,Berlin\n4,Rome\n")
    return str(p)


@pytest.fixture
def file_c_extra(tmp_path):
    p = tmp_path / "c.csv"
    p.write_text("id,city,country\n5,Madrid,Spain\n")
    return str(p)


def test_full_pipeline_two_files(file_a, file_b, tmp_path):
    out_path = str(tmp_path / "merged.csv")
    readers = [StreamingCSVReader(file_a), StreamingCSVReader(file_b)]
    merged = merge_rows([r.iter_rows() for r in readers])
    writer = StreamingCSVWriter(out_path)
    writer.write_rows(merged)
    assert writer.rows_written == 4
    content = open(out_path).read()
    assert "London" in content
    assert "Berlin" in content


def test_full_pipeline_with_extra_column(file_a, file_c_extra, tmp_path):
    out_path = str(tmp_path / "merged.csv")
    readers = [StreamingCSVReader(file_a), StreamingCSVReader(file_c_extra)]
    merged = merge_rows([r.iter_rows() for r in readers], fill_value="unknown")
    writer = StreamingCSVWriter(out_path)
    writer.write_rows(merged)
    assert writer.rows_written == 3
    content = open(out_path).read()
    assert "unknown" in content
    assert "Spain" in content


def test_full_pipeline_preserves_row_count(file_a, file_b, file_c_extra, tmp_path):
    out_path = str(tmp_path / "merged.csv")
    readers = [
        StreamingCSVReader(file_a),
        StreamingCSVReader(file_b),
        StreamingCSVReader(file_c_extra),
    ]
    merged = merge_rows([r.iter_rows() for r in readers])
    writer = StreamingCSVWriter(out_path)
    writer.write_rows(merged)
    assert writer.rows_written == 5
