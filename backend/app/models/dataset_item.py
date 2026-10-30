from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey, Index, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.result import Result


class DatasetItem(Base):
    __tablename__ = "dataset_items"
    __table_args__ = (Index("ix_dataset_items_dataset_id_position", "dataset_id", "position"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"))
    position: Mapped[int] = mapped_column(Integer)
    input_prompt: Mapped[str] = mapped_column(Text)
    expected_output: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict] = mapped_column("metadata", JSON)

    dataset: Mapped["Dataset"] = relationship(back_populates="items")
    results: Mapped[list["Result"]] = relationship(back_populates="item", passive_deletes="all")
