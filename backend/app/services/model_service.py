from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Model, User, UserRole


class DuplicateModelNameError(Exception):
    pass


class ModelInUseError(Exception):
    pass


def is_admin(user: User) -> bool:
    return user.role == UserRole.ADMIN


async def create_model(session: AsyncSession, data: dict[str, Any]) -> Model:
    model = Model(**data)
    session.add(model)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if _is_duplicate_model_name_error(exc):
            raise DuplicateModelNameError("model_name already exists")
        raise

    await session.refresh(model)
    return model


async def list_models_for_user(session: AsyncSession, user: User) -> list[Model]:
    query = select(Model).order_by(Model.updated_at.desc())
    if not is_admin(user):
        query = query.where(Model.is_active.is_(True))

    result = await session.execute(query)
    return list(result.scalars().all())


async def get_model_by_id_for_user(session: AsyncSession, model_id: uuid.UUID, user: User) -> Model | None:
    query = select(Model).where(Model.id == model_id)
    if not is_admin(user):
        query = query.where(Model.is_active.is_(True))

    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_model_by_id(session: AsyncSession, model_id: uuid.UUID) -> Model | None:
    result = await session.execute(select(Model).where(Model.id == model_id))
    return result.scalar_one_or_none()


async def update_model(session: AsyncSession, model: Model, data: dict[str, Any]) -> Model:
    for key, value in data.items():
        setattr(model, key, value)

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if _is_duplicate_model_name_error(exc):
            raise DuplicateModelNameError("model_name already exists")
        raise

    await session.refresh(model)
    return model


async def delete_model(session: AsyncSession, model: Model) -> None:
    await session.delete(model)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise ModelInUseError("Model is in use and cannot be deleted.") from exc


def _is_duplicate_model_name_error(exc: IntegrityError) -> bool:
    original = getattr(exc, "orig", None)
    if original is None:
        return False

    message = str(original).lower()
    if "unique constraint failed" in message and "models.model_name" in message:
        return True

    sqlstate = getattr(original, "sqlstate", None)
    return sqlstate == "23505"
