from decimal import Decimal

from evaluation.measurement.aggregation import aggregate
from tests.measurement.conftest import scored


def _answers():
    return [
        scored("m", "lookup", 0, "5", {"a": 5, "b": 5}),
        scored("m", "lookup", 1, "3", {"a": 3, "b": 3}),
        scored("m", "uncovered", 2, "4", {"a": 4, "b": 4}),
    ]


def test_overall_mean_and_stddev() -> None:
    model = aggregate(_answers())["m"]

    assert model.overall.mean == Decimal("4.000")
    assert model.overall.stddev == Decimal("1.000")
    assert model.overall.count == 3


def test_per_category_breakdown() -> None:
    model = aggregate(_answers())["m"]

    assert model.per_category["lookup"].mean == Decimal("4.000")
    assert model.per_category["lookup"].stddev == Decimal("1.414")
    assert model.per_category["uncovered"].mean == Decimal("4.000")
    assert model.per_category["uncovered"].stddev == Decimal("0.000")


def test_per_criterion_breakdown() -> None:
    model = aggregate(_answers())["m"]

    assert model.per_criterion["a"].mean == Decimal("4.000")
    assert model.per_category_criterion["lookup"]["a"].mean == Decimal("4.000")
