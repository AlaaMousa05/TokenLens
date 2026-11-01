from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base

if TYPE_CHECKING:
    from app.models.model import Model
    from app.models.run import Run


class RunModel(Base):
    __tablename__ = "run_models"

    run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("runs.id"), primary_key=True)
    model_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("models.id"), primary_key=True)

    run: Mapped["Run"] = relationship(back_populates="run_models")
    model: Mapped["Model"] = relationship(back_populates="run_models")
