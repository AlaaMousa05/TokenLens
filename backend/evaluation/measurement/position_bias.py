"""Position bias from swapped pairwise comparisons: how often order alone flips the verdict."""

from dataclasses import dataclass
from decimal import Decimal

from evaluation.judging.verdict import JudgmentStatus, PairwiseJudgment

_PLACES = Decimal("0.001")


@dataclass(frozen=True)
class PositionBiasReport:
    """Flip rate across pairwise comparisons that were each run in both orders."""

    comparisons: int
    flips: int
    flip_rate: Decimal


def position_bias(outcomes: list[PairwiseJudgment]) -> PositionBiasReport:
    """A flip is a comparison whose winner did not survive swapping A and B."""
    scored = [outcome for outcome in outcomes if outcome.status is JudgmentStatus.ok]
    if not scored:
        return PositionBiasReport(comparisons=0, flips=0, flip_rate=Decimal("0"))
    flips = sum(1 for outcome in scored if not outcome.verdict_survives_swap)
    flip_rate = (Decimal(flips) / len(scored)).quantize(_PLACES)
    return PositionBiasReport(comparisons=len(scored), flips=flips, flip_rate=flip_rate)
