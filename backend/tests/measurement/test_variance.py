from decimal import Decimal

from evaluation.measurement.variance import summarize_variance


def test_spread_and_noise_of_repeated_judgments() -> None:
    summary = summarize_variance([Decimal("4"), Decimal("5"), Decimal("4")])

    assert summary.minimum == Decimal("4")
    assert summary.maximum == Decimal("5")
    assert summary.spread == Decimal("1")
    assert summary.stat.mean == Decimal("4.333")
    assert summary.stat.count == 3
