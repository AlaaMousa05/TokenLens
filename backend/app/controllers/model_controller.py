from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse
from app.schemas.model_schema import ModelCreateRequest, ModelPublic, ModelUpdateRequest
from app.services.model_service import (
    DuplicateModelNameError,
    create_model,
    delete_model,
    get_model_by_id,
    get_model_by_id_for_user,
    is_admin,
    list_models_for_user,
    ModelInUseError,
    update_model,
)

router = APIRouter(prefix="/models", tags=["models"])


def _to_model_public(model) -> ModelPublic:
    return ModelPublic(
        id=model.id,
        provider=model.provider,
        model_name=model.model_name,
        display_name=model.display_name,
        input_price_per_mtok=model.input_price_per_mtok,
        output_price_per_mtok=model.output_price_per_mtok,
        context_window=model.context_window,
        is_active=model.is_active,
        updated_at=model.updated_at,
    )


@router.post(
    "",
    response_model=ModelPublic,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        403: {"model": ErrorResponse, "description": "Admins only."},
        409: {"model": ErrorResponse, "description": "model_name already exists."},
        422: {"description": "Validation error."},
    },
)
async def create_new_model(
    payload: ModelCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ModelPublic:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    try:
        model = await create_model(session, payload.model_dump())
    except DuplicateModelNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return _to_model_public(model)


@router.get(
    "",
    response_model=list[ModelPublic],
    responses={401: {"model": ErrorResponse, "description": "Unauthorized."}},
)
async def list_models(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> list[ModelPublic]:
    models = await list_models_for_user(session, current_user)
    return [_to_model_public(model) for model in models]


@router.get(
    "/{model_id}",
    response_model=ModelPublic,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        404: {"model": ErrorResponse, "description": "Model not found."},
    },
)
async def get_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ModelPublic:
    model = await get_model_by_id_for_user(session, model_id, current_user)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")
    return _to_model_public(model)


@router.patch(
    "/{model_id}",
    response_model=ModelPublic,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        403: {"model": ErrorResponse, "description": "Admins only."},
        404: {"model": ErrorResponse, "description": "Model not found."},
        409: {"model": ErrorResponse, "description": "model_name already exists."},
        422: {"description": "Validation error."},
    },
)
async def patch_model(
    model_id: uuid.UUID,
    payload: ModelUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ModelPublic:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    model = await get_model_by_id(session, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")

    updates = payload.model_dump(exclude_unset=True)
    try:
        model = await update_model(session, model, updates)
    except DuplicateModelNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return _to_model_public(model)


@router.delete(
    "/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    response_model=None,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized."},
        403: {"model": ErrorResponse, "description": "Admins only."},
        404: {"model": ErrorResponse, "description": "Model not found."},
        409: {"model": ErrorResponse, "description": "Model is in use and cannot be deleted."},
    },
)
async def remove_model(
    model_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    if not is_admin(current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    model = await get_model_by_id(session, model_id)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model not found")

    try:
        await delete_model(session, model)
    except ModelInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
