import pytest
from csv_surgeon.classifier import build_rule, classify_rows


@pytest.fixture
def sample_rows():
    return [
        {"name": "Alice", "age": "30", "score": "85"},
        {"name": "Bob", "age": "17", "score": "55"},
        {"name": "Carol", "age": "45", "score": "95"},
        {"name": "Dave", "age": "22", "score": "40"},
    ]


def test_classify_assigns_first_matching_label(sample_rows):
    rules = [
        build_rule("high", "score", "gte", "80"),
        build_rule("mid", "score", "gte", "50"),
        build_rule("low", "score", "lt", "50"),
    ]
    result = list(classify_rows(sample_rows, rules))
    assert result[0]["class"] == "high"
    assert result[1]["class"] == "mid"
    assert result[2]["class"] == "high"
    assert result[3]["class"] == "low"


def test_classify_default_when_no_rule_matches(sample_rows):
    rules = [build_rule("senior", "age", "gte", "40")]
    result = list(classify_rows(sample_rows, rules, default="other"))
    assert result[0]["class"] == "other"
    assert result[2]["class"] == "senior"


def test_classify_custom_output_column(sample_rows):
    rules = [build_rule("minor", "age", "lt", "18")]
    result = list(classify_rows(sample_rows, rules, output_column="category", default="adult"))
    assert "category" in result[0]
    assert result[1]["category"] == "minor"
    assert result[0]["category"] == "adult"


def test_classify_preserves_original_fields(sample_rows):
    rules = [build_rule("x", "score", "gt", "0")]
    result = list(classify_rows(sample_rows, rules))
    assert result[0]["name"] == "Alice"
    assert result[0]["age"] == "30"


def test_classify_eq_operator(sample_rows):
    rules = [build_rule("alice", "name", "eq", "Alice")]
    result = list(classify_rows(sample_rows, rules))
    assert result[0]["class"] == "alice"
    assert result[1]["class"] == ""


def test_classify_contains_operator(sample_rows):
    rules = [build_rule("has_a", "name", "contains", "a")]
    result = list(classify_rows(sample_rows, rules))
    assert result[2]["class"] == "has_a"  # Carol
    assert result[0]["class"] == ""       # Alice (capital A)


def test_classify_neq_operator(sample_rows):
    rules = [build_rule("not_alice", "name", "neq", "Alice")]
    result = list(classify_rows(sample_rows, rules))
    assert result[0]["class"] == ""
    assert result[1]["class"] == "not_alice"


def test_classify_empty_rules_uses_default(sample_rows):
    result = list(classify_rows(sample_rows, [], default="unknown"))
    assert all(r["class"] == "unknown" for r in result)


def test_classify_empty_stream():
    rules = [build_rule("x", "col", "eq", "val")]
    result = list(classify_rows([], rules))
    assert result == []


def test_build_rule_invalid_operator():
    import pytest
    with pytest.raises(ValueError, match="Unknown operator"):
        build_rule("label", "col", "unknown", "val")
