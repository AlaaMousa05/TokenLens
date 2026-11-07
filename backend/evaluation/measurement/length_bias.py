"""Length bias: does the judge reward the longer of two equally-correct answers?

The pairs are derived from answers the models actually produced — two answers to
the same question that earned an identical weighted total but differ in length —
never written by hand, and the selection rule is reported with the result.
"""

from dataclasses import dataclass
from decimal import Decimal
from itertools import combinations

from evaluation.judging.verdict import JudgmentStatus, PairwiseChoice, PairwiseJudgment
from evaluation.measurement.records import ScoredAnswer

_PLACES = Decimal("0.001")

# Below this many decisive comparisons, a preference rate is too noisy to trust —
# a single flipped comparison swings it by double digits.
MINIMUM_DECISIVE_PAIRS = 10


@dataclass(frozen=True)
class LengthPair:
    """Two equally-scored answers to one question; `longer` is presented as answer A."""

    row_id: int
    weighted_total: Decimal
    longer: ScoredAnswer
    shorter: ScoredAnswer


@dataclass(frozen=True)
class LengthBiasReport:
    """How often the longer answer won among decisive, order-consistent comparisons."""

    decisive: int
    longer_preferred: int
    longer_preference_rate: Decimal
    selection: str

    @property
    def underpowered(self) -> bool:
        return self.decisive < MINIMUM_DECISIVE_PAIRS


def build_length_pairs(answers: list[ScoredAnswer], minimum_length_ratio: Decimal = Decimal("0.25")) -> tuple[list[LengthPair], str]:
    """Pairs of same-row answers with identical weighted total whose lengths differ enough."""
    selection = (
        "Pairs are two models' answers to the same question with an identical weighted total "
        f"(equivalent correctness) whose output-token lengths differ by at least {minimum_length_ratio:.0%}; "
        "the longer answer is presented as A."
    )
    by_row: dict[int, list[ScoredAnswer]] = {}
    for answer in answers:
        by_row.setdefault(answer.row_id, []).append(answer)

    pairs: list[LengthPair] = []
    for row_id, row_answers in by_row.items():
        for first, second in combinations(row_answers, 2):
            if first.model_name == second.model_name or first.weighted_total != second.weighted_total:
                continue
            longer, shorter = (first, second) if first.length >= second.length else (second, first)
            if shorter.length == 0 or longer.length < shorter.length * (1 + minimum_length_ratio):
                continue
            pairs.append(LengthPair(row_id=row_id, weighted_total=longer.weighted_total, longer=longer, shorter=shorter))
    return pairs, selection


def longer_won(outcome: PairwiseJudgment) -> bool | None:
    """With the longer answer as A: True if it won consistently, False if the shorter did, None if inconclusive."""
    if outcome.status is not JudgmentStatus.ok or not outcome.verdict_survives_swap:
        return None
    if outcome.original.overall is PairwiseChoice.a:
        return True
    if outcome.original.overall is PairwiseChoice.b:
        return False
    return None


def summarize_length_bias(outcomes: list[bool | None], selection: str) -> LengthBiasReport:
    """Rate at which the longer answer was preferred among decisive comparisons."""
    longer = sum(1 for outcome in outcomes if outcome is True)
    shorter = sum(1 for outcome in outcomes if outcome is False)
    decisive = longer + shorter
    rate = (Decimal(longer) / decisive).quantize(_PLACES) if decisive else Decimal("0")
    return LengthBiasReport(decisive=decisive, longer_preferred=longer, longer_preference_rate=rate, selection=selection)
