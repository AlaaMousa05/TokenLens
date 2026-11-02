from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse
from app.schemas.rubric_schema import (
    RubricCreateRequest,
    RubricListResponse,
    RubricPublic,
    RubricUpdateRequest,
)
from app.services.rubric_service import (
    RubricInUseError,
    create_rubric,
    delete_rubric,
    get_user_rubric,
    list_user_rubrics,
    update_rubric,
)

router = APIRouter(prefix="/rubrics", tags=["rubrics"])


def _to_rubric_public(rubric) -> RubricPublic:
    return RubricPublic(
        id=rubric.id,
        name=rubric.name,
        criteria=rubric.criteria,
        scale_min=rubric.scale_min,
        scale_max=rubric.scale_max,
        judge_instructions=rubric.judge_instructions,
        created_at=rubric.created_at,
    )


@router.post(
    "",
    response_model=RubricPublic,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 422: {"description": "Validation error."}},
)
async def create_rubric_endpoint(
    payload: RubricCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RubricPublic:
    try:
        rubric = await create_rubric(
            session=session,
            owner_id=current_user.id,
            name=payload.name,
            criteria=payload.criteria,
            scale_min=payload.scale_min,
            scale_max=payload.scale_max,
            judge_instructions=payload.judge_instructions,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return _to_rubric_public(rubric)


@router.get("", response_model=RubricListResponse, responses={401: {"model": ErrorResponse}})
async def list_rubrics_endpoint(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RubricListResponse:
    if page < 1 or size < 1 or size > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page>=1 and 1<=size<=100 are required")

    items, total = await list_user_rubrics(session, current_user.id, page, size)
    return RubricListResponse(items=[_to_rubric_public(item) for item in items], page=page, size=size, total=total)


@router.get(
    "/{rubric_id}",
    response_model=RubricPublic,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_rubric_endpoint(
    rubric_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RubricPublic:
    rubric = await get_user_rubric(session, current_user.id, rubric_id)
    if rubric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found")
    return _to_rubric_public(rubric)


@router.patch(
    "/{rubric_id}",
    response_model=RubricPublic,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"description": "Validation error."}},
)
async def update_rubric_endpoint(
    rubric_id: uuid.UUID,
    payload: RubricUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RubricPublic:
    rubric = await get_user_rubric(session, current_user.id, rubric_id)
    if rubric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found")

    try:
        rubric = await update_rubric(session, rubric, payload.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return _to_rubric_public(rubric)


@router.delete(
    "/{rubric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def delete_rubric_endpoint(
    rubric_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    rubric = await get_user_rubric(session, current_user.id, rubric_id)
    if rubric is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rubric not found")

    try:
        await delete_rubric(session, rubric)
    except RubricInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
