from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import get_current_user
from app.dbconfig import get_db_session
from app.models.entities import User
from app.schemas.auth_schema import ErrorResponse
from app.schemas.run_schema import (
    JudgmentForResult,
    RunCreateRequest,
    RunListResponse,
    RunPublic,
    RunResultPublic,
    RunResultsResponse,
)
from app.services.run_service import (
    RunValidationError,
    create_run,
    get_user_run,
    list_run_results,
    list_user_runs,
)

router = APIRouter(prefix="/runs", tags=["runs"])


def _to_run_public(run, model_ids: list[uuid.UUID]) -> RunPublic:
    return RunPublic(
        id=run.id,
        user_id=run.user_id,
        dataset_id=run.dataset_id,
        rubric_id=run.rubric_id,
        baseline_run_id=run.baseline_run_id,
        judge_model_id=run.judge_model_id,
        name=run.name,
        repeats=run.repeats,
        temperature=run.temperature,
        swap_order=run.swap_order,
        status=run.status,
        total_cost_usd=run.total_cost_usd,
        created_at=run.created_at,
        finished_at=run.finished_at,
        model_ids=model_ids,
    )


@router.post(
    "",
    response_model=RunPublic,
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}, 422: {"description": "Validation error."}},
)
async def create_run_endpoint(
    payload: RunCreateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RunPublic:
    try:
        created = await create_run(
            session=session,
            user_id=current_user.id,
            name=payload.name,
            dataset_id=payload.dataset_id,
            rubric_id=payload.rubric_id,
            model_ids=payload.model_ids,
            judge_model_id=payload.judge_model_id,
            repeats=payload.repeats,
            temperature=payload.temperature,
            swap_order=payload.swap_order,
        )
    except RunValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return _to_run_public(created.run, created.model_ids)


@router.get("", response_model=RunListResponse, responses={401: {"model": ErrorResponse}})
async def list_runs_endpoint(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RunListResponse:
    if page < 1 or size < 1 or size > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page>=1 and 1<=size<=100 are required")

    rows, total = await list_user_runs(session, current_user.id, page, size)
    return RunListResponse(items=[_to_run_public(row.run, row.model_ids) for row in rows], page=page, size=size, total=total)


@router.get(
    "/{run_id}",
    response_model=RunPublic,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_run_endpoint(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RunPublic:
    run_with_models = await get_user_run(session, current_user.id, run_id)
    if run_with_models is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return _to_run_public(run_with_models.run, run_with_models.model_ids)


@router.get(
    "/{run_id}/results",
    response_model=RunResultsResponse,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_run_results_endpoint(
    run_id: uuid.UUID,
    page: int = 1,
    size: int = 50,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RunResultsResponse:
    if page < 1 or size < 1 or size > 200:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="page>=1 and 1<=size<=200 are required")

    run_with_models = await get_user_run(session, current_user.id, run_id)
    if run_with_models is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")

    rows, judgments_map, total = await list_run_results(session, run_id, page, size)
    items: list[RunResultPublic] = []
    for result, position, question_text, model_display_name in rows:
        judgments = judgments_map.get(result.id, [])
        items.append(
            RunResultPublic(
                id=result.id,
                item_id=result.item_id,
                question_text=question_text,
                position=position,
                model_id=result.model_id,
                model_display_name=model_display_name,
                repeat_index=result.repeat_index,
                output_text=result.output_text,
                input_tokens=result.input_tokens,
                output_tokens=result.output_tokens,
                latency_ms=result.latency_ms,
                cost_usd=result.cost_usd,
                status=result.status,
                error_message=result.error_message,
                attempts=result.attempts,
                judgments=[
                    JudgmentForResult(
                        id=judgment.id,
                        score=judgment.score,
                        criteria_scores=judgment.criteria_scores,
                        reasoning=judgment.reasoning,
                        judge_cost_usd=judgment.judge_cost_usd,
                    )
                    for judgment in judgments
                ],
            )
        )

    return RunResultsResponse(items=items, page=page, size=size, total=total)
