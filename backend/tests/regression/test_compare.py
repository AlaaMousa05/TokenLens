from decimal import Decimal

from evaluation.measurement.aggregation import aggregate
from evaluation.regression.compare import compare_to_golden
from evaluation.regression.golden import freeze_golden
from evaluation.regression.threshold import derive_threshold
from tests.measurement.conftest import make_run, scored

_THRESHOLD = derive_threshold(Decimal("0.140"))


def _golden():
    baseline = aggregate([scored("m", "lookup", 0, "5", {"a": 5, "b": 5})])
    return freeze_golden(make_run([]).manifest, baseline)


def test_drop_beyond_threshold_alerts_and_names_worst_criterion() -> None:
    current = aggregate([scored("m", "lookup", 0, "4", {"a": 4, "b": 3})])

    alerts = compare_to_golden(_golden(), current, _THRESHOLD)

    assert len(alerts) == 1
    assert alerts[0].model_name == "m"
    assert alerts[0].category == "lookup"
    assert alerts[0].drop == Decimal("1.000")
    assert alerts[0].worst_criterion == "b"
    assert alerts[0].worst_criterion_drop == Decimal("2.000")


def test_drop_within_judge_noise_does_not_alert() -> None:
    current = aggregate([scored("m", "lookup", 0, "4.9", {"a": 5, "b": 5})])

    assert compare_to_golden(_golden(), current, _THRESHOLD) == []
