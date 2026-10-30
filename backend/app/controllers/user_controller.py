from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse, UserPublic
from app.services.user_service import get_all_users, get_user_by_id, is_admin

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "",
    response_model=list[UserPublic],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        403: {"model": ErrorResponse, "description": "Admins only."},
    },
)
async def list_users(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[UserPublic]:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    users = await get_all_users(session)
    return [
        UserPublic(id=user.id, name=user.name, email=user.email, role=user.role, created_at=user.created_at)
        for user in users
    ]


@router.get(
    "/{user_id}",
    response_model=UserPublic,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        403: {"model": ErrorResponse, "description": "Admins only."},
        404: {"model": ErrorResponse, "description": "User not found."},
    },
)
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> UserPublic:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserPublic(id=user.id, name=user.name, email=user.email, role=user.role, created_at=user.created_at)
