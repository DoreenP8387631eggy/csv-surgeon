import pytest
from csv_surgeon.transform import (
    TransformPipeline,
    rename_column,
    add_column,
    drop_column,
    map_column,
)


@pytest.fixture
def pipeline():
    return TransformPipeline()


@pytest.fixture
def sample_row():
    return {"name": "Alice", "age": "30", "city": "Berlin"}


def test_rename_column(pipeline, sample_row):
    pipeline.add_transform(rename_column("name", "full_name"))
    result = pipeline.apply(dict(sample_row))
    assert "full_name" in result
    assert "name" not in result
    assert result["full_name"] == "Alice"


def test_rename_missing_column_is_noop(pipeline, sample_row):
    pipeline.add_transform(rename_column("nonexistent", "other"))
    result = pipeline.apply(dict(sample_row))
    assert result == sample_row


def test_drop_column(pipeline, sample_row):
    pipeline.add_transform(drop_column("city"))
    result = pipeline.apply(dict(sample_row))
    assert "city" not in result
    assert "name" in result


def test_drop_missing_column_is_noop(pipeline, sample_row):
    pipeline.add_transform(drop_column("missing"))
    result = pipeline.apply(dict(sample_row))
    assert result == sample_row


def test_map_column(pipeline, sample_row):
    pipeline.add_transform(map_column("name", str.upper))
    result = pipeline.apply(dict(sample_row))
    assert result["name"] == "ALICE"


def test_add_column(pipeline, sample_row):
    pipeline.add_transform(add_column("greeting", lambda r: f"Hello, {r['name']}"))
    result = pipeline.apply(dict(sample_row))
    assert result["greeting"] == "Hello, Alice"


def test_chained_transforms(pipeline, sample_row):
    pipeline.add_transform(map_column("age", lambda v: str(int(v) + 1)))
    pipeline.add_transform(rename_column("age", "age_next_year"))
    pipeline.add_transform(drop_column("city"))
    result = pipeline.apply(dict(sample_row))
    assert result["age_next_year"] == "31"
    assert "age" not in result
    assert "city" not in result


def test_apply_all(pipeline):
    rows = [
        {"val": "1"},
        {"val": "2"},
        {"val": "3"},
    ]
    pipeline.add_transform(map_column("val", lambda v: str(int(v) * 10)))
    results = list(pipeline.apply_all(rows))
    assert [r["val"] for r in results] == ["10", "20", "30"]


def test_clear_transforms(pipeline, sample_row):
    pipeline.add_transform(map_column("name", str.upper))
    pipeline.clear_transforms()
    result = pipeline.apply(dict(sample_row))
    assert result["name"] == "Alice"
