from decimal import Decimal

from evaluation.regression.threshold import derive_threshold


def test_threshold_is_two_times_judge_noise_with_stated_derivation() -> None:
    threshold = derive_threshold(Decimal("0.140"))

    assert threshold.value == Decimal("0.280")
    assert "0.140" in threshold.derivation
    assert "0.280" in threshold.derivation


def test_zero_noise_is_floored_rather_than_producing_a_zero_threshold() -> None:
    threshold = derive_threshold(Decimal("0.000"))

    assert threshold.value == Decimal("0.250")
    assert threshold.value > Decimal("0")
    assert "floored" in threshold.derivation


def test_noise_above_the_floor_is_unaffected_by_it() -> None:
    threshold = derive_threshold(Decimal("1.000"))

    assert threshold.value == Decimal("2.000")
    assert "floored" not in threshold.derivation
