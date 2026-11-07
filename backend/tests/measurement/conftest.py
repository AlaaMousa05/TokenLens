from datetime import datetime, timezone
from decimal import Decimal

from evaluation.contracts import CallStatus, CompletionOutcome, ModelResponse, PriceSnapshot
from evaluation.judging.verdict import (
    CriterionVerdict,
    Judgment,
    JudgmentStatus,
    PairwiseChoice,
    PairwiseJudgment,
    PairwiseVerdict,
    Verdict,
)
from evaluation.measurement.records import FullRun, ResultRecord, RunManifest, ScoredAnswer

_SNAPSHOT = PriceSnapshot(
    input_price_per_mtok=Decimal("1.00"),
    output_price_per_mtok=Decimal("2.00"),
    cached_input_price_per_mtok=None,
    captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)


def scored(model_name, category, row_id, total, scores, length=50) -> ScoredAnswer:
    return ScoredAnswer(
        model_name=model_name,
        category=category,
        row_id=row_id,
        weighted_total=Decimal(total),
        criterion_scores=scores,
        length=length,
    )


def make_response(input_tokens: int, output_tokens: int) -> ModelResponse:
    return ModelResponse(
        output_text="x",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=1,
        attempts=1,
        status=CallStatus.ok,
        completion_outcome=CompletionOutcome.normal,
        tokens_estimated=False,
        prices_snapshot=_SNAPSHOT,
    )


def make_pairwise(survives: bool, overall: PairwiseChoice = PairwiseChoice.a, ok: bool = True) -> PairwiseJudgment:
    if not ok:
        return PairwiseJudgment(status=JudgmentStatus.failed, error_message="boom")
    verdict = PairwiseVerdict(overall=overall, rationale="r")
    return PairwiseJudgment(
        status=JudgmentStatus.ok,
        original=verdict,
        swapped=verdict,
        verdict_survives_swap=survives,
        shows_position_bias=not survives,
    )


def make_record(model_name, row_id, category, question, answer, scores, total) -> ResultRecord:
    verdict = Verdict(
        scores={name: CriterionVerdict(score=value, rationale="r") for name, value in scores.items()},
        overall_note="n",
    )
    judgment = Judgment(
        status=JudgmentStatus.ok,
        verdict=verdict,
        weighted_total=Decimal(total),
        rubric_name="customer_support_default",
        rubric_version=1,
        attempts=1,
    )
    return ResultRecord(
        row_id=row_id,
        category=category,
        model_name=model_name,
        repeat=0,
        question=question,
        reference="ref",
        candidate_answer=answer,
        response=make_response(10, 5),
        judgment=judgment,
    )


def make_run(records) -> FullRun:
    manifest = RunManifest(
        dataset_version="abc123",
        rubric_name="customer_support_default",
        rubric_version=1,
        judge_model="Llama-3.3-70B-Instruct",
        repeats=1,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        total_cost=Decimal("0"),
        total_tokens=0,
    )
    return FullRun(manifest=manifest, records=records)
