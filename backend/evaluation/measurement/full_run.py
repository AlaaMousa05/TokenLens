"""Runs the whole dataset against the compared models with N repeats, judged once each.

Every candidate response and verdict is collected into a FullRun; totals come from
a usage recorder wrapping the shared client, so they cover candidate and judge calls.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from evaluation.contracts import ModelSpec
from evaluation.judging.judge import Judge
from evaluation.judging.rubric import Rubric
from evaluation.measurement.records import FullRun, ResultRecord, RunManifest, dataset_version
from evaluation.measurement.usage import UsageRecorder

_CANDIDATE_MAX_TOKENS = 512


@dataclass(frozen=True)
class DatasetRow:
    """One dataset question with its reference answer and category."""

    row_id: int
    question: str
    reference: str
    category: str


async def run_dataset(
    recorder: UsageRecorder,
    judge: Judge,
    judge_model: str,
    candidate_models: list[ModelSpec],
    policy: str,
    rows: list[DatasetRow],
    repeats: int,
    rubric: Rubric,
    dataset_path: Path,
) -> FullRun:
    """Score every (model, row, repeat) and return the collected run with its manifest."""
    records: list[ResultRecord] = []
    for model in candidate_models:
        for row in rows:
            for repeat in range(repeats):
                answer = await recorder.complete(model, row.question, policy, 0.0, _CANDIDATE_MAX_TOKENS)
                judgment = await judge.score(policy, row.question, row.reference, answer.output_text)
                records.append(
                    ResultRecord(
                        row_id=row.row_id,
                        category=row.category,
                        model_name=model.model_name,
                        repeat=repeat,
                        question=row.question,
                        reference=row.reference,
                        candidate_answer=answer.output_text,
                        response=answer,
                        judgment=judgment,
                    )
                )
    manifest = RunManifest(
        dataset_version=dataset_version(dataset_path),
        rubric_name=rubric.name,
        rubric_version=rubric.version,
        judge_model=judge_model,
        repeats=repeats,
        created_at=datetime.now(timezone.utc),
        total_cost=recorder.total_cost,
        total_tokens=recorder.total_tokens,
    )
    return FullRun(manifest=manifest, records=records)
