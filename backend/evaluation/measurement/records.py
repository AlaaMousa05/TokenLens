"""Persisted raw run data and the lightweight projection the analyses consume.

The raw data (every candidate response and every verdict) outlives the session,
so an analysis can be re-run from the JSON file without re-calling the APIs.
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from pydantic import BaseModel, Field

from evaluation.contracts import ModelResponse
from evaluation.judging.verdict import Judgment, JudgmentStatus


class ResultRecord(BaseModel):
    """One candidate answer and its verdict, with the metadata to trace it to a dataset row."""

    row_id: int
    category: str
    model_name: str
    repeat: int
    question: str
    reference: str
    candidate_answer: str
    response: ModelResponse
    judgment: Judgment


class RunManifest(BaseModel):
    """The reproducibility header printed with every report."""

    dataset_version: str = Field(description="Short hash of the dataset file, so a changed dataset is a new version.")
    rubric_name: str
    rubric_version: int
    judge_model: str
    repeats: int
    created_at: datetime
    total_cost: Decimal
    total_tokens: int


class FullRun(BaseModel):
    """A manifest plus every result from one run."""

    manifest: RunManifest
    records: list[ResultRecord]


@dataclass(frozen=True)
class ScoredAnswer:
    """Projection of one successful verdict for aggregation, variance and bias analysis."""

    model_name: str
    category: str
    row_id: int
    weighted_total: Decimal
    criterion_scores: dict[str, int]
    length: int


def scored_answers(run: FullRun) -> list[ScoredAnswer]:
    """Project the successful verdicts; failed judgments carry no score and are skipped."""
    answers: list[ScoredAnswer] = []
    for record in run.records:
        if record.judgment.status is not JudgmentStatus.ok or record.judgment.verdict is None:
            continue
        answers.append(
            ScoredAnswer(
                model_name=record.model_name,
                category=record.category,
                row_id=record.row_id,
                weighted_total=record.judgment.weighted_total,
                criterion_scores={name: verdict.score for name, verdict in record.judgment.verdict.scores.items()},
                length=record.response.output_tokens,
            )
        )
    return answers


def dataset_version(dataset_path: Path) -> str:
    """Short content hash of the dataset file."""
    return hashlib.sha256(dataset_path.read_bytes()).hexdigest()[:12]
