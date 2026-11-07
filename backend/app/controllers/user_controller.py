from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse, UserProfileUpdateRequest, UserPublic, UserRoleUpdateRequest
from app.services.user_service import get_all_users, get_user_by_id, is_admin, update_user

router = APIRouter(prefix="/users", tags=["users"])


def _to_user_public(user: User) -> UserPublic:
    return UserPublic(id=user.id, name=user.name, email=user.email, role=user.role, created_at=user.created_at)


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
    return [_to_user_public(user) for user in users]


@router.patch(
    "/me",
    response_model=UserPublic,
    responses={
        400: {"model": ErrorResponse, "description": "No fields to update."},
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        422: {"description": "Validation error."},
    },
)
async def patch_me(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> UserPublic:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    if "name" in updates:
        updates["name"] = str(updates["name"]).strip()
        if not updates["name"]:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Name must not be blank")

    user = await update_user(session, current_user, updates)
    return _to_user_public(user)


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

    return _to_user_public(user)


@router.patch(
    "/{user_id}/role",
    response_model=UserPublic,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        403: {"model": ErrorResponse, "description": "Admins only."},
        404: {"model": ErrorResponse, "description": "User not found."},
        422: {"description": "Validation error."},
    },
)
async def patch_user_role(
    user_id: uuid.UUID,
    payload: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> UserPublic:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    user = await get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user = await update_user(session, user, {"role": payload.role})
    return _to_user_public(user)
