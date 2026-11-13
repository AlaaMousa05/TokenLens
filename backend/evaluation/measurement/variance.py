"""Run-to-run variance of the judge on a fixed answer.

Judging the same answer N times isolates judge noise from model difference: no
score gap between two models is real unless it exceeds this noise.
"""

from dataclasses import dataclass
from decimal import Decimal

from evaluation.measurement.statistics import Stat, summarize


@dataclass(frozen=True)
class VarianceSummary:
    """Spread of repeated judgments of one fixed answer."""

    stat: Stat
    minimum: Decimal
    maximum: Decimal

    @property
    def spread(self) -> Decimal:
        return self.maximum - self.minimum


def summarize_variance(scores: list[Decimal]) -> VarianceSummary:
    """Summarize repeated weighted totals for the same answer; stddev here is the judge's noise."""
    return VarianceSummary(stat=summarize(scores), minimum=min(scores), maximum=max(scores))
