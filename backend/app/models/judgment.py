from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Numeric, SmallInteger, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base

if TYPE_CHECKING:
    from app.models.model import Model
    from app.models.result import Result


class Judgment(Base):
    __tablename__ = "judgments"
    __table_args__ = (
        UniqueConstraint("result_id", "order_variant", name="uq_judgment_result_order_variant"),
        CheckConstraint("order_variant IN (0, 1)", name="ck_judgment_order_variant"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("results.id"))
    judge_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"))
    order_variant: Mapped[int] = mapped_column(SmallInteger)
    score: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    criteria_scores: Mapped[dict] = mapped_column(JSON)
    reasoning: Mapped[str] = mapped_column(Text)
    judge_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    result: Mapped["Result"] = relationship(back_populates="judgments")
    judge_model: Mapped["Model"] = relationship(back_populates="judgments")
