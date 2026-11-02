from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Numeric, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base

if TYPE_CHECKING:
    from app.models.model import Model
    from app.models.run import Run


class RegressionAlert(Base):
    __tablename__ = "regression_alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"))
    baseline_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"))
    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"))
    baseline_score: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    new_score: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    delta: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    threshold: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped["Run"] = relationship(back_populates="regression_alerts", foreign_keys=[run_id])
    baseline_run: Mapped["Run"] = relationship(back_populates="baseline_alerts", foreign_keys=[baseline_run_id])
    model: Mapped["Model"] = relationship(back_populates="regression_alerts")
