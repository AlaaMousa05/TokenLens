from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum as SqlEnum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base
from app.models.enums import UserRole, enum_values

if TYPE_CHECKING:
    from app.models.dataset import Dataset
    from app.models.rubric import Rubric
    from app.models.run import Run


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole, name="user_role", values_callable=enum_values))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    datasets: Mapped[list["Dataset"]] = relationship(back_populates="owner", passive_deletes="all")
    rubrics: Mapped[list["Rubric"]] = relationship(back_populates="owner", passive_deletes="all")
    runs: Mapped[list["Run"]] = relationship(back_populates="user", passive_deletes="all")
