"""Structured judge output and the stored judgment result.

The judge returns only per-criterion scores and rationales; the weighted total
is computed in Python, never reported by the model.
"""

from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class CriterionVerdict(BaseModel):
    """One criterion's score and the judge's one-sentence reason."""

    model_config = ConfigDict(extra="forbid")

    score: int = Field(ge=1, le=5, description="Score on the 1-5 rubric scale.")
    rationale: str = Field(min_length=1, description="One sentence justifying the score.")


class Verdict(BaseModel):
    """The judge's structured reply for scoring one answer."""

    model_config = ConfigDict(extra="forbid")

    scores: dict[str, CriterionVerdict] = Field(description="Per-criterion verdicts, keyed by criterion name.")
    overall_note: str = Field(min_length=1, description="One-sentence summary; not a score.")


class PairwiseChoice(str, Enum):
    """Which answer a pairwise comparison prefers."""

    a = "A"
    b = "B"
    tie = "tie"


class PairwiseVerdict(BaseModel):
    """The judge's structured reply for comparing answer A against answer B."""

    model_config = ConfigDict(extra="forbid")

    overall: PairwiseChoice = Field(description="Which answer is better overall.")
    rationale: str = Field(min_length=1, description="One sentence justifying the choice.")


class JudgmentStatus(str, Enum):
    """Whether a judgment produced a usable verdict."""

    ok = "ok"
    failed = "failed"


class Judgment(BaseModel):
    """The stored outcome of scoring one answer: per-criterion scores kept, never only the total."""

    status: JudgmentStatus
    verdict: Verdict | None = Field(default=None, description="Present only when status is ok.")
    weighted_total: Decimal | None = Field(default=None, description="Computed in Python from the scores.")
    rubric_name: str
    rubric_version: int
    attempts: int = Field(description="Judge calls made, including the one retry on invalid output.")
    error_message: str | None = Field(default=None, description="Set only when status is failed.")


class PairwiseJudgment(BaseModel):
    """Two comparisons of the same pair with A/B swapped, and whether the winner survived the swap."""

    status: JudgmentStatus
    original: PairwiseVerdict | None = Field(default=None, description="Verdict with the answers in input order.")
    swapped: PairwiseVerdict | None = Field(default=None, description="Verdict with the answers exchanged.")
    verdict_survives_swap: bool | None = Field(
        default=None, description="True if both orders chose the same underlying answer (or both tied)."
    )
    shows_position_bias: bool | None = Field(
        default=None, description="True if both orders chose the same position (A then A, or B then B)."
    )
    error_message: str | None = Field(default=None, description="Set only when status is failed.")
