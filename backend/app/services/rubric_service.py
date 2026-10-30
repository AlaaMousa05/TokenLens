from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Rubric, Run


class RubricInUseError(Exception):
    pass


def _normalize_judge_instructions(value: str | None) -> str:
    return (value or "").strip()


def validate_rubric_values(criteria: list[dict], scale_min: int, scale_max: int) -> None:
    if len(criteria) == 0:
        raise ValueError("criteria must contain at least one item.")

    for index, criterion in enumerate(criteria, start=1):
        if not isinstance(criterion, dict):
            raise ValueError(f"criteria[{index}] must be an object.")

        weight = criterion.get("weight")
        if weight is not None:
            if not isinstance(weight, (int, float)):
                raise ValueError(f"criteria[{index}].weight must be a number.")
            if weight <= 0:
                raise ValueError(f"criteria[{index}].weight must be greater than zero.")

    if scale_min > scale_max:
        raise ValueError("scale_min must be less than or equal to scale_max.")


async def create_rubric(
    session: AsyncSession,
    owner_id: uuid.UUID,
    name: str,
    criteria: list[dict],
    scale_min: int,
    scale_max: int,
    judge_instructions: str | None,
) -> Rubric:
    validate_rubric_values(criteria, scale_min, scale_max)

    rubric = Rubric(
        owner_id=owner_id,
        name=name.strip(),
        criteria=criteria,
        scale_min=scale_min,
        scale_max=scale_max,
        judge_instructions=_normalize_judge_instructions(judge_instructions),
    )
    session.add(rubric)
    await session.commit()
    await session.refresh(rubric)
    return rubric


async def list_user_rubrics(
    session: AsyncSession,
    owner_id: uuid.UUID,
    page: int,
    size: int,
) -> tuple[list[Rubric], int]:
    total = await session.scalar(select(func.count()).select_from(Rubric).where(Rubric.owner_id == owner_id)) or 0
    offset = (page - 1) * size
    rows = await session.execute(
        select(Rubric)
        .where(Rubric.owner_id == owner_id)
        .order_by(Rubric.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    return list(rows.scalars().all()), total


async def get_user_rubric(session: AsyncSession, owner_id: uuid.UUID, rubric_id: uuid.UUID) -> Rubric | None:
    row = await session.execute(
        select(Rubric).where(Rubric.owner_id == owner_id, Rubric.id == rubric_id)
    )
    return row.scalar_one_or_none()


async def update_rubric(session: AsyncSession, rubric: Rubric, updates: dict) -> Rubric:
    final_name = updates["name"].strip() if "name" in updates and updates["name"] is not None else rubric.name
    final_criteria = updates["criteria"] if "criteria" in updates and updates["criteria"] is not None else rubric.criteria
    final_scale_min = updates["scale_min"] if "scale_min" in updates and updates["scale_min"] is not None else rubric.scale_min
    final_scale_max = updates["scale_max"] if "scale_max" in updates and updates["scale_max"] is not None else rubric.scale_max
    final_judge_instructions = (
        _normalize_judge_instructions(updates["judge_instructions"])
        if "judge_instructions" in updates
        else rubric.judge_instructions
    )

    validate_rubric_values(final_criteria, final_scale_min, final_scale_max)

    rubric.name = final_name
    rubric.criteria = final_criteria
    rubric.scale_min = final_scale_min
    rubric.scale_max = final_scale_max
    rubric.judge_instructions = final_judge_instructions

    await session.commit()
    await session.refresh(rubric)
    return rubric


async def delete_rubric(session: AsyncSession, rubric: Rubric) -> None:
    run_exists = await session.scalar(select(func.count()).select_from(Run).where(Run.rubric_id == rubric.id)) or 0
    if run_exists > 0:
        raise RubricInUseError("Rubric has been used in runs and cannot be deleted.")

    await session.delete(rubric)
    await session.commit()
