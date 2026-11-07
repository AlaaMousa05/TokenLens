"""A frozen golden baseline: what a later run is measured against.

Captures the dataset version, rubric version, judge, repeat count and every
per-criterion score (as per-category means with their spread), so a regression
check compares like against like.
"""

from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel

from evaluation.measurement.aggregation import ModelAggregate
from evaluation.measurement.records import RunManifest
from evaluation.measurement.statistics import Stat


class StatRecord(BaseModel):
    """A persisted mean, standard deviation and count."""

    mean: Decimal
    stddev: Decimal
    count: int


class ModelBaseline(BaseModel):
    """One model's frozen per-category total and per-category per-criterion means."""

    per_category_total: dict[str, StatRecord]
    per_category_criterion: dict[str, dict[str, StatRecord]]


class GoldenBaseline(BaseModel):
    """A run frozen for regression comparison."""

    dataset_version: str
    rubric_name: str
    rubric_version: int
    judge_model: str
    repeats: int
    created_at: datetime
    models: dict[str, ModelBaseline]


def _record(stat: Stat) -> StatRecord:
    return StatRecord(mean=stat.mean, stddev=stat.stddev, count=stat.count)


def freeze_golden(manifest: RunManifest, aggregates: dict[str, ModelAggregate]) -> GoldenBaseline:
    """Freeze a run's manifest and aggregates into a golden baseline."""
    models = {
        name: ModelBaseline(
            per_category_total={category: _record(stat) for category, stat in aggregate.per_category.items()},
            per_category_criterion={
                category: {criterion: _record(stat) for criterion, stat in criteria.items()}
                for category, criteria in aggregate.per_category_criterion.items()
            },
        )
        for name, aggregate in aggregates.items()
    }
    return GoldenBaseline(
        dataset_version=manifest.dataset_version,
        rubric_name=manifest.rubric_name,
        rubric_version=manifest.rubric_version,
        judge_model=manifest.judge_model,
        repeats=manifest.repeats,
        created_at=manifest.created_at,
        models=models,
    )


def save_golden(golden: GoldenBaseline, path: Path) -> None:
    """Write the golden baseline to JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(golden.model_dump_json(indent=2), encoding="utf-8")


def load_golden(path: Path) -> GoldenBaseline:
    """Read a golden baseline from JSON."""
    return GoldenBaseline.model_validate_json(path.read_text(encoding="utf-8"))
