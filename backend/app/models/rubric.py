from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base

if TYPE_CHECKING:
    from app.models.run import Run
    from app.models.user import User


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    criteria: Mapped[list[dict]] = mapped_column(JSON)
    scale_min: Mapped[int] = mapped_column(SmallInteger)
    scale_max: Mapped[int] = mapped_column(SmallInteger)
    judge_instructions: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="rubrics")
    runs: Mapped[list["Run"]] = relationship(back_populates="rubric", passive_deletes="all")
