from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey, String, Text, false, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.dbconfig import Base
from app.models.enums import SourceFormat, enum_values

if TYPE_CHECKING:
    from app.models.dataset_item import DatasetItem
    from app.models.run import Run
    from app.models.user import User


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    source_format: Mapped[SourceFormat] = mapped_column(
        SqlEnum(SourceFormat, name="source_format", values_callable=enum_values)
    )
    is_golden: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped["User"] = relationship(back_populates="datasets")
    items: Mapped[list["DatasetItem"]] = relationship(back_populates="dataset", passive_deletes="all")
    runs: Mapped[list["Run"]] = relationship(back_populates="dataset", passive_deletes="all")
