from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, func, true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base

if TYPE_CHECKING:
    from app.models.judgment import Judgment
    from app.models.regression_alert import RegressionAlert
    from app.models.result import Result
    from app.models.run import Run
    from app.models.run_model import RunModel


class Model(Base):
    """Model catalog prices are in USD per million tokens."""

    __tablename__ = "models"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(120), unique=True)
    display_name: Mapped[str] = mapped_column(String(120))
    input_price_per_mtok: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    output_price_per_mtok: Mapped[Decimal] = mapped_column(Numeric(10, 4))
    context_window: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    run_models: Mapped[list["RunModel"]] = relationship(back_populates="model", passive_deletes="all")
    evaluation_runs: Mapped[list["Run"]] = relationship(
        secondary="run_models", back_populates="evaluated_models", viewonly=True
    )
    judged_runs: Mapped[list["Run"]] = relationship(back_populates="judge_model", passive_deletes="all")
    results: Mapped[list["Result"]] = relationship(back_populates="model", passive_deletes="all")
    judgments: Mapped[list["Judgment"]] = relationship(back_populates="judge_model", passive_deletes="all")
    regression_alerts: Mapped[list["RegressionAlert"]] = relationship(
        back_populates="model", passive_deletes="all"
    )
