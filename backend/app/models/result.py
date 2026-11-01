from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Index, Integer, Numeric, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base
from app.models.enums import ResultStatus, enum_values

if TYPE_CHECKING:
    from app.models.dataset_item import DatasetItem
    from app.models.judgment import Judgment
    from app.models.model import Model
    from app.models.run import Run


class Result(Base):
    __tablename__ = "results"
    __table_args__ = (
        UniqueConstraint("run_id", "item_id", "model_id", "repeat_index", name="uq_result_run_item_model_repeat"),
        Index("ix_results_run_id_model_id", "run_id", "model_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"))
    item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("dataset_items.id"))
    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"))
    repeat_index: Mapped[int] = mapped_column(SmallInteger)
    output_text: Mapped[str] = mapped_column(Text)
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    latency_ms: Mapped[int] = mapped_column(Integer)
    cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    status: Mapped[ResultStatus] = mapped_column(
        SqlEnum(ResultStatus, name="result_status", values_callable=enum_values)
    )
    error_message: Mapped[str | None] = mapped_column(Text)
    attempts: Mapped[int] = mapped_column(SmallInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped["Run"] = relationship(back_populates="results")
    item: Mapped["DatasetItem"] = relationship(back_populates="results")
    model: Mapped["Model"] = relationship(back_populates="results")
    judgments: Mapped[list["Judgment"]] = relationship(back_populates="result", passive_deletes="all")
