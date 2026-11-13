"""Blind scoring-sheet construction and judge/human agreement.

The sheet carries candidate answers with empty criterion columns, in randomised
order with model identity removed, so a human can score blind. Agreement is
reported per criterion, including how often the two differ by more than one point.
"""

import random
from dataclasses import dataclass
from decimal import Decimal

from evaluation.judging.verdict import JudgmentStatus
from evaluation.measurement.records import FullRun

_PLACES = Decimal("0.001")


@dataclass(frozen=True)
class SheetRow:
    """One blind row: an opaque id and the answer to score, with no model identity."""

    sheet_id: int
    question: str
    candidate_answer: str


@dataclass(frozen=True)
class CriterionAgreement:
    """How a judge and a human agreed on one criterion."""

    criterion: str
    compared: int
    exact_rate: Decimal
    within_one_rate: Decimal
    over_one_rate: Decimal


def build_scoring_sheet(run: FullRun, seed: int) -> tuple[list[SheetRow], dict[int, dict[str, int]]]:
    """Return shuffled blind rows and the judge's scores keyed by the same sheet ids."""
    scored = [record for record in run.records if record.judgment.status is JudgmentStatus.ok]
    order = list(range(len(scored)))
    random.Random(seed).shuffle(order)

    rows: list[SheetRow] = []
    judge_scores: dict[int, dict[str, int]] = {}
    for sheet_id, index in enumerate(order, start=1):
        record = scored[index]
        rows.append(SheetRow(sheet_id=sheet_id, question=record.question, candidate_answer=record.candidate_answer))
        judge_scores[sheet_id] = {name: verdict.score for name, verdict in record.judgment.verdict.scores.items()}
    return rows, judge_scores


def compute_agreement(
    judge_scores: dict[int, dict[str, int]],
    human_scores: dict[int, dict[str, int]],
    criteria: list[str],
) -> list[CriterionAgreement]:
    """Per-criterion agreement over the sheet ids both sides scored."""
    shared = sorted(set(judge_scores) & set(human_scores))
    return [_criterion_agreement(name, shared, judge_scores, human_scores) for name in criteria]


def _criterion_agreement(
    name: str,
    shared: list[int],
    judge_scores: dict[int, dict[str, int]],
    human_scores: dict[int, dict[str, int]],
) -> CriterionAgreement:
    differences = [
        abs(judge_scores[sheet_id][name] - human_scores[sheet_id][name])
        for sheet_id in shared
        if name in judge_scores[sheet_id] and name in human_scores[sheet_id]
    ]
    compared = len(differences)
    if compared == 0:
        return CriterionAgreement(name, 0, Decimal("0"), Decimal("0"), Decimal("0"))
    exact = sum(1 for difference in differences if difference == 0)
    within_one = sum(1 for difference in differences if difference <= 1)
    over_one = sum(1 for difference in differences if difference > 1)
    return CriterionAgreement(
        criterion=name,
        compared=compared,
        exact_rate=(Decimal(exact) / compared).quantize(_PLACES),
        within_one_rate=(Decimal(within_one) / compared).quantize(_PLACES),
        over_one_rate=(Decimal(over_one) / compared).quantize(_PLACES),
    )
