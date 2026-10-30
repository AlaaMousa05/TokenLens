from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, Index, Numeric, SmallInteger, String, false, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base
from app.models.enums import RunStatus, enum_values

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.model import Model
    from app.models.regression_alert import RegressionAlert
    from app.models.result import Result
    from app.models.rubric import Rubric
    from app.models.run_model import RunModel
    from app.models.user import User


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"))
    rubric_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("rubrics.id"))
    baseline_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("runs.id"))
    judge_model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"))
    name: Mapped[str] = mapped_column(String(150))
    repeats: Mapped[int] = mapped_column(SmallInteger)
    temperature: Mapped[Decimal] = mapped_column(Numeric(3, 2))
    swap_order: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    status: Mapped[RunStatus] = mapped_column(SqlEnum(RunStatus, name="run_status", values_callable=enum_values))
    total_cost_usd: Mapped[Decimal] = mapped_column(Numeric(12, 6))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship(back_populates="runs")
    dataset: Mapped["Dataset"] = relationship(back_populates="runs")
    rubric: Mapped["Rubric"] = relationship(back_populates="runs")
    judge_model: Mapped["Model"] = relationship(back_populates="judged_runs", foreign_keys=[judge_model_id])
    baseline_run: Mapped["Run | None"] = relationship(
        back_populates="compared_runs", foreign_keys=[baseline_run_id], remote_side=[id]
    )
    compared_runs: Mapped[list["Run"]] = relationship(
        back_populates="baseline_run", foreign_keys=[baseline_run_id], passive_deletes="all"
    )
    run_models: Mapped[list["RunModel"]] = relationship(back_populates="run", passive_deletes="all")
    evaluated_models: Mapped[list["Model"]] = relationship(
        secondary="run_models", back_populates="evaluation_runs", viewonly=True
    )
    results: Mapped[list["Result"]] = relationship(back_populates="run", passive_deletes="all")
    regression_alerts: Mapped[list["RegressionAlert"]] = relationship(
        back_populates="run", foreign_keys="RegressionAlert.run_id", passive_deletes="all"
    )
    baseline_alerts: Mapped[list["RegressionAlert"]] = relationship(
        back_populates="baseline_run", foreign_keys="RegressionAlert.baseline_run_id", passive_deletes="all"
    )


Index("ix_runs_user_id_created_at_desc", Run.user_id, Run.created_at.desc())
