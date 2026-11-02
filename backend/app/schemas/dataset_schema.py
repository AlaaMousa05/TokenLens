import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.entities import SourceFormat


class DatasetItemPublic(BaseModel):
    id: uuid.UUID
    position: int
    input: str
    expected_output: str | None


class DatasetPromptCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    input: str = Field(min_length=1)
    expected_output: str | None = None


class DatasetPromptCreateResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    source_format: SourceFormat
    is_golden: bool
    created_at: datetime
    item: DatasetItemPublic


class DatasetUploadResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_format: SourceFormat
    item_count: int


class DatasetSummary(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    source_format: SourceFormat
    is_golden: bool
    created_at: datetime
    item_count: int


class DatasetListResponse(BaseModel):
    items: list[DatasetSummary]
    page: int
    size: int
    total: int


class DatasetUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    is_golden: bool | None = None


class DatasetItemListResponse(BaseModel):
    items: list[DatasetItemPublic]
    page: int
    size: int
    total: int


class DatasetItemCreateRequest(BaseModel):
    input: str = Field(min_length=1)
    expected_output: str | None = None


class DatasetItemUpdateRequest(BaseModel):
    input: str | None = None
    expected_output: str | None = None
