import pytest
from csv_surgeon.binner import bin_equal_width, bin_custom, bin_labels


@pytest.fixture
def sample_rows():
    return [
        {"name": "a", "score": "10"},
        {"name": "b", "score": "35"},
        {"name": "c", "score": "60"},
        {"name": "d", "score": "85"},
        {"name": "e", "score": "100"},
    ]


def test_bin_equal_width_adds_column(sample_rows):
    result = list(bin_equal_width(sample_rows, "score", 4, 0, 100))
    assert all("bin" in r for r in result)


def test_bin_equal_width_correct_count(sample_rows):
    result = list(bin_equal_width(sample_rows, "score", 4, 0, 100))
    assert len(result) == 5


def test_bin_equal_width_first_row_bin(sample_rows):
    result = list(bin_equal_width(sample_rows, "score", 4, 0, 100))
    assert result[0]["bin"] == "[0, 25)"


def test_bin_equal_width_last_row_bin(sample_rows):
    result = list(bin_equal_width(sample_rows, "score", 4, 0, 100))
    assert result[4]["bin"] == "[75, 100)"


def test_bin_equal_width_custom_out_col(sample_rows):
    result = list(bin_equal_width(sample_rows, "score", 2, 0, 100, out_col="range"))
    assert "range" in result[0]


def test_bin_equal_width_non_numeric_uses_default(sample_rows):
    rows = [{"score": "n/a"}]
    result = list(bin_equal_width(rows, "score", 4, 0, 100, default="unknown"))
    assert result[0]["bin"] == "unknown"


def test_bin_equal_width_preserves_other_columns(sample_rows):
    result = list(bin_equal_width(sample_rows, "score", 4, 0, 100))
    assert result[0]["name"] == "a"


def test_bin_custom_assigns_correct_label():
    rows = [{"v": "15"}, {"v": "45"}, {"v": "75"}]
    edges = [0, 30, 60, 100]
    labels = ["low", "mid", "high"]
    result = list(bin_custom(rows, "v", edges, labels))
    assert result[0]["bin"] == "low"
    assert result[1]["bin"] == "mid"
    assert result[2]["bin"] == "high"


def test_bin_custom_auto_labels():
    rows = [{"v": "5"}]
    result = list(bin_custom(rows, "v", [0, 10, 20]))
    assert result[0]["bin"] == "[0, 10)"


def test_bin_custom_non_numeric_default():
    rows = [{"v": "abc"}]
    result = list(bin_custom(rows, "v", [0, 10], default="?"))
    assert result[0]["bin"] == "?"


def test_bin_custom_preserves_fields():
    rows = [{"v": "5", "x": "keep"}]
    result = list(bin_custom(rows, "v", [0, 10]))
    assert result[0]["x"] == "keep"


def test_bin_labels_assigns_first_matching():
    rows = [{"score": "20"}, {"score": "55"}, {"score": "90"}]
    thresholds = [(30, "low"), (60, "mid"), (100, "high")]
    result = list(bin_labels(rows, "score", thresholds))
    assert result[0]["bin"] == "low"
    assert result[1]["bin"] == "mid"
    assert result[2]["bin"] == "high"


def test_bin_labels_default_when_no_match():
    rows = [{"score": "999"}]
    thresholds = [(100, "ok")]
    result = list(bin_labels(rows, "score", thresholds, default="extreme"))
    assert result[0]["bin"] == "extreme"


def test_bin_labels_non_numeric_uses_default():
    rows = [{"score": ""}]
    result = list(bin_labels(rows, "score", [(100, "ok")], default="?"))
    assert result[0]["bin"] == "?"
