"""Compare a run against a golden baseline, per model and category.

An alert is raised only when a category's weighted-total drop exceeds the
noise-derived threshold; it names the criterion that fell most.
"""

from dataclasses import dataclass
from decimal import Decimal

from evaluation.measurement.aggregation import ModelAggregate
from evaluation.regression.golden import GoldenBaseline
from evaluation.regression.threshold import Threshold


@dataclass(frozen=True)
class RegressionAlert:
    """A category whose quality dropped beyond the threshold, and the criterion most responsible."""

    model_name: str
    category: str
    baseline_total: Decimal
    current_total: Decimal
    drop: Decimal
    worst_criterion: str
    worst_criterion_drop: Decimal


def compare_to_golden(
    golden: GoldenBaseline,
    current: dict[str, ModelAggregate],
    threshold: Threshold,
) -> list[RegressionAlert]:
    """Alert on each model/category whose weighted-total mean fell by more than the threshold."""
    alerts: list[RegressionAlert] = []
    for model_name, baseline in golden.models.items():
        aggregate = current.get(model_name)
        if aggregate is None:
            continue
        for category, baseline_total in baseline.per_category_total.items():
            current_total = aggregate.per_category.get(category)
            if current_total is None:
                continue
            drop = baseline_total.mean - current_total.mean
            if drop <= threshold.value:
                continue
            criterion, criterion_drop = _worst_criterion(baseline, aggregate, category)
            alerts.append(
                RegressionAlert(
                    model_name=model_name,
                    category=category,
                    baseline_total=baseline_total.mean,
                    current_total=current_total.mean,
                    drop=drop,
                    worst_criterion=criterion,
                    worst_criterion_drop=criterion_drop,
                )
            )
    return alerts


def _worst_criterion(baseline, aggregate: ModelAggregate, category: str) -> tuple[str, Decimal]:
    baseline_criteria = baseline.per_category_criterion.get(category, {})
    current_criteria = aggregate.per_category_criterion.get(category, {})
    worst_name = ""
    worst_drop = Decimal("-999")
    for name, baseline_stat in baseline_criteria.items():
        current_stat = current_criteria.get(name)
        if current_stat is None:
            continue
        drop = baseline_stat.mean - current_stat.mean
        if drop > worst_drop:
            worst_name, worst_drop = name, drop
    return worst_name, worst_drop
