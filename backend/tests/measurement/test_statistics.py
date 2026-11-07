from decimal import Decimal

import pytest

from evaluation.measurement.statistics import summarize


def test_mean_and_sample_stddev() -> None:
    stat = summarize([Decimal("4"), Decimal("5")])

    assert stat.mean == Decimal("4.500")
    assert stat.stddev == Decimal("0.707")
    assert stat.count == 2


def test_single_value_has_zero_stddev() -> None:
    stat = summarize([Decimal("3")])

    assert stat.mean == Decimal("3.000")
    assert stat.stddev == Decimal("0.000")


def test_empty_is_rejected() -> None:
    with pytest.raises(ValueError):
        summarize([])
