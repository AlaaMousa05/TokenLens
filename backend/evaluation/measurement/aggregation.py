"""Per-model aggregation of weighted totals and per-criterion scores.

Every figure is a mean paired with its standard deviation, broken down per
category and per criterion.
"""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from evaluation.measurement.records import ScoredAnswer
from evaluation.measurement.statistics import Stat, summarize


@dataclass(frozen=True)
class ModelAggregate:
    """One model's scores summarized overall, per category, per criterion, and per category-criterion."""

    model_name: str
    overall: Stat
    per_category: dict[str, Stat]
    per_criterion: dict[str, Stat]
    per_category_criterion: dict[str, dict[str, Stat]]


def aggregate(answers: list[ScoredAnswer]) -> dict[str, ModelAggregate]:
    """Summarize weighted totals and per-criterion scores for each model."""
    by_model: dict[str, list[ScoredAnswer]] = defaultdict(list)
    for answer in answers:
        by_model[answer.model_name].append(answer)
    return {model: _aggregate_model(model, group) for model, group in by_model.items()}


def _aggregate_model(model_name: str, answers: list[ScoredAnswer]) -> ModelAggregate:
    criteria = sorted({name for answer in answers for name in answer.criterion_scores})
    return ModelAggregate(
        model_name=model_name,
        overall=summarize([answer.weighted_total for answer in answers]),
        per_category=_by_category(answers),
        per_criterion={name: summarize(_criterion_scores(answers, name)) for name in criteria},
        per_category_criterion=_by_category_criterion(answers, criteria),
    )


def _by_category(answers: list[ScoredAnswer]) -> dict[str, Stat]:
    grouped: dict[str, list[Decimal]] = defaultdict(list)
    for answer in answers:
        grouped[answer.category].append(answer.weighted_total)
    return {category: summarize(totals) for category, totals in grouped.items()}


def _by_category_criterion(answers: list[ScoredAnswer], criteria: list[str]) -> dict[str, dict[str, Stat]]:
    categories = sorted({answer.category for answer in answers})
    result: dict[str, dict[str, Stat]] = {}
    for category in categories:
        in_category = [answer for answer in answers if answer.category == category]
        result[category] = {name: summarize(_criterion_scores(in_category, name)) for name in criteria}
    return result


def _criterion_scores(answers: list[ScoredAnswer], name: str) -> list[Decimal]:
    return [Decimal(answer.criterion_scores[name]) for answer in answers if name in answer.criterion_scores]
