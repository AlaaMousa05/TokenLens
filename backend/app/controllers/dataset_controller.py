from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse
from app.schemas.dataset_schema import (
    DatasetItemCreateRequest,
    DatasetItemListResponse,
    DatasetItemPublic,
    DatasetItemUpdateRequest,
    DatasetListResponse,
    DatasetPromptCreateRequest,
    DatasetPromptCreateResponse,
    DatasetSummary,
    DatasetUpdateRequest,
    DatasetUploadResponse,
)
from app.services.dataset_service import (
    DatasetInUseError,
    DatasetLimitError,
    FileValidationError,
    create_dataset_item,
    create_prompt_dataset,
    create_uploaded_dataset,
    delete_dataset_item,
    delete_user_dataset,
    get_dataset_item,
    get_user_dataset,
    list_dataset_items,
    list_user_datasets,
    parse_uploaded_questions,
    update_dataset_item,
    update_user_dataset,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _to_dataset_summary(dataset, item_count: int) -> DatasetSummary:
    return DatasetSummary(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        source_format=dataset.source_format,
        is_golden=dataset.is_golden,
        created_at=dataset.created_at,
        item_count=item_count,
    )


def _to_item_public(item) -> DatasetItemPublic:
    return DatasetItemPublic(
        id=item.id,
        position=item.position,
        input=item.input_prompt,
        expected_output=item.expected_output,
    )


@router.post(
    "/prompt",
    response_model=DatasetPromptCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 422: {"description": "Validation error."}},
)
async def create_prompt_dataset_endpoint(
    payload: DatasetPromptCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetPromptCreateResponse:
    try:
        dataset, item = await create_prompt_dataset(
            session=session,
            owner_id=current_user.id,
            name=payload.name,
            description=payload.description,
            input_text=payload.input,
            expected_output=payload.expected_output,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return DatasetPromptCreateResponse(
        id=dataset.id,
        name=dataset.name,
        description=dataset.description,
        source_format=dataset.source_format,
        is_golden=dataset.is_golden,
        created_at=dataset.created_at,
        item=_to_item_public(item),
    )


@router.post(
    "/upload",
    response_model=DatasetUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def upload_dataset_endpoint(
    name: str = Form(...),
    description: str | None = Form(default=None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetUploadResponse:
    content = await file.read()
    try:
        source_format, questions = parse_uploaded_questions(file.filename, content)
    except FileValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"errors": exc.errors})

    dataset = await create_uploaded_dataset(
        session=session,
        owner_id=current_user.id,
        name=name,
        description=description,
        source_format=source_format,
        questions=questions,
    )

    return DatasetUploadResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        item_count=len(questions),
    )


@router.get("", response_model=DatasetListResponse, responses={401: {"model": ErrorResponse}})
async def list_datasets_endpoint(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetListResponse:
    if page < 1 or size < 1 or size > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page>=1 and 1<=size<=100 are required")

    rows, total = await list_user_datasets(session, current_user.id, page, size)
    return DatasetListResponse(
        items=[_to_dataset_summary(dataset, item_count) for dataset, item_count in rows],
        page=page,
        size=size,
        total=total,
    )


@router.get(
    "/{dataset_id}",
    response_model=DatasetSummary,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_dataset_endpoint(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetSummary:
    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    dataset, item_count = row
    return _to_dataset_summary(dataset, item_count)


@router.patch(
    "/{dataset_id}",
    response_model=DatasetSummary,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 422: {"description": "Validation error."}},
)
async def update_dataset_endpoint(
    dataset_id: uuid.UUID,
    payload: DatasetUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetSummary:
    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    dataset, _ = row

    updates = payload.model_dump(exclude_unset=True)
    dataset = await update_user_dataset(session, dataset, updates)
    refreshed = await get_user_dataset(session, current_user.id, dataset_id)
    assert refreshed is not None
    return _to_dataset_summary(refreshed[0], refreshed[1])


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def delete_dataset_endpoint(
    dataset_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    dataset, _ = row

    try:
        await delete_user_dataset(session, dataset)
    except DatasetInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/{dataset_id}/items",
    response_model=DatasetItemListResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def list_dataset_items_endpoint(
    dataset_id: uuid.UUID,
    page: int = 1,
    size: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetItemListResponse:
    if page < 1 or size < 1 or size > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page>=1 and 1<=size<=200 are required")

    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    items, total = await list_dataset_items(session, dataset_id, page, size)
    return DatasetItemListResponse(items=[_to_item_public(item) for item in items], page=page, size=size, total=total)


@router.post(
    "/{dataset_id}/items",
    response_model=DatasetItemPublic,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def create_dataset_item_endpoint(
    dataset_id: uuid.UUID,
    payload: DatasetItemCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetItemPublic:
    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    try:
        item = await create_dataset_item(session, dataset_id, payload.input, payload.expected_output)
    except DatasetLimitError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return _to_item_public(item)


@router.patch(
    "/{dataset_id}/items/{item_id}",
    response_model=DatasetItemPublic,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def update_dataset_item_endpoint(
    dataset_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: DatasetItemUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> DatasetItemPublic:
    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    item = await get_dataset_item(session, dataset_id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    updates = payload.model_dump(exclude_unset=True)
    try:
        item = await update_dataset_item(session, item, updates)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return _to_item_public(item)


@router.delete(
    "/{dataset_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def delete_dataset_item_endpoint(
    dataset_id: uuid.UUID,
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> None:
    row = await get_user_dataset(session, current_user.id, dataset_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    item = await get_dataset_item(session, dataset_id, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    await delete_dataset_item(session, item)
