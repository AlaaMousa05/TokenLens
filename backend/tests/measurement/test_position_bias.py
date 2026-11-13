from decimal import Decimal

from evaluation.measurement.position_bias import position_bias
from tests.measurement.conftest import make_pairwise


def test_flip_rate_counts_verdicts_that_do_not_survive_swap() -> None:
    outcomes = [make_pairwise(survives=True), make_pairwise(survives=False), make_pairwise(survives=True)]

    report = position_bias(outcomes)

    assert report.comparisons == 3
    assert report.flips == 1
    assert report.flip_rate == Decimal("0.333")


def test_failed_comparisons_are_excluded() -> None:
    report = position_bias([make_pairwise(survives=True), make_pairwise(survives=False, ok=False)])

    assert report.comparisons == 1
    assert report.flips == 0
