import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.entities import ResultStatus, RunStatus


class RunCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    dataset_id: uuid.UUID
    rubric_id: uuid.UUID
    model_ids: list[uuid.UUID] = Field(min_length=2, max_length=8)
    judge_model_id: uuid.UUID
    repeats: int = Field(default=1, ge=1, le=5)
    temperature: float = Field(default=0, ge=0, le=2)
    swap_order: bool = False

    @field_validator("model_ids")
    @classmethod
    def unique_model_ids(cls, value: list[uuid.UUID]) -> list[uuid.UUID]:
        if len(set(value)) != len(value):
            raise ValueError("model_ids must contain unique values.")
        return value


class RunPublic(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    dataset_id: uuid.UUID
    rubric_id: uuid.UUID
    baseline_run_id: uuid.UUID | None
    judge_model_id: uuid.UUID
    name: str
    repeats: int
    temperature: Decimal
    swap_order: bool
    status: RunStatus
    total_cost_usd: Decimal
    created_at: datetime
    finished_at: datetime | None
    model_ids: list[uuid.UUID]


class RunListResponse(BaseModel):
    items: list[RunPublic]
    page: int
    size: int
    total: int


class JudgmentForResult(BaseModel):
    id: uuid.UUID
    score: Decimal
    criteria_scores: dict
    reasoning: str
    judge_cost_usd: Decimal


class RunResultPublic(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID
    question_text: str
    position: int
    model_id: uuid.UUID
    model_display_name: str
    repeat_index: int
    output_text: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cost_usd: Decimal
    status: ResultStatus
    error_message: str | None
    attempts: int
    judgments: list[JudgmentForResult]


class RunResultsResponse(BaseModel):
    items: list[RunResultPublic]
    page: int
    size: int
    total: int
