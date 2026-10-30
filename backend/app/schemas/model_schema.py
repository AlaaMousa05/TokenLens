import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ModelCreateRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=50)
    model_name: str = Field(min_length=1, max_length=120)
    display_name: str = Field(min_length=1, max_length=120)
    input_price_per_mtok: Decimal = Field(ge=0)
    output_price_per_mtok: Decimal = Field(ge=0)
    context_window: int = Field(gt=0)
    is_active: bool = True


class ModelUpdateRequest(BaseModel):
    provider: str | None = Field(default=None, min_length=1, max_length=50)
    model_name: str | None = Field(default=None, min_length=1, max_length=120)
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    input_price_per_mtok: Decimal | None = Field(default=None, ge=0)
    output_price_per_mtok: Decimal | None = Field(default=None, ge=0)
    context_window: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class ModelPublic(BaseModel):
    id: uuid.UUID
    provider: str
    model_name: str
    display_name: str
    input_price_per_mtok: Decimal
    output_price_per_mtok: Decimal
    context_window: int
    is_active: bool
    updated_at: datetime
