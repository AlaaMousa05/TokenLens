import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class RubricCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    criteria: list[dict]
    scale_min: int
    scale_max: int
    judge_instructions: str | None = None


class RubricUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    criteria: list[dict] | None = None
    scale_min: int | None = None
    scale_max: int | None = None
    judge_instructions: str | None = None


class RubricPublic(BaseModel):
    id: uuid.UUID
    name: str
    criteria: list[dict]
    scale_min: int
    scale_max: int
    judge_instructions: str
    created_at: datetime


class RubricListResponse(BaseModel):
    items: list[RubricPublic]
    page: int
    size: int
    total: int
