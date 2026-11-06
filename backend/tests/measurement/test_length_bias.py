from decimal import Decimal

from evaluation.measurement.length_bias import build_length_pairs, summarize_length_bias
from tests.measurement.conftest import scored


def test_pairs_are_equal_score_different_length_different_model() -> None:
    answers = [
        scored("A", "lookup", 0, "4", {"a": 4}, length=100),
        scored("B", "lookup", 0, "4", {"a": 4}, length=50),
        scored("C", "lookup", 1, "5", {"a": 5}, length=100),
        scored("D", "lookup", 1, "5", {"a": 5}, length=95),
    ]

    pairs, selection = build_length_pairs(answers)

    assert len(pairs) == 1
    assert pairs[0].row_id == 0
    assert pairs[0].longer.model_name == "A"
    assert pairs[0].shorter.model_name == "B"
    assert "equivalent correctness" in selection


def test_longer_preference_rate_over_decisive_comparisons() -> None:
    report = summarize_length_bias([True, False, True, None], selection="s")

    assert report.decisive == 3
    assert report.longer_preferred == 2
    assert report.longer_preference_rate == Decimal("0.667")


def test_fewer_than_ten_decisive_pairs_is_underpowered() -> None:
    report = summarize_length_bias([True, False, True, None], selection="s")

    assert report.underpowered is True


def test_ten_or_more_decisive_pairs_is_not_underpowered() -> None:
    report = summarize_length_bias([True] * 10, selection="s")

    assert report.underpowered is False
