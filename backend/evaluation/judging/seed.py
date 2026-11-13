"""Seeds the default demo dataset and rubric so a fresh install has something to run against.

Both inserts are idempotent: skipped if a row with the same name already exists.
Owned by the earliest-registered user; skips entirely if no user exists yet,
so startup never fails over missing seed data.
"""

import csv
from pathlib import Path

from sqlalchemy import select

from app.models.entities import Dataset, DatasetItem, Rubric, SourceFormat, User
from evaluation.judging.rubric import default_support_rubric

_DATASET_NAME = "Nimbus Support Q&A"
_RUBRIC_NAME = "Support Quality"
_RUBRIC_INSTRUCTIONS = "Score each criterion independently. Be strict on policy adherence."
_QUESTIONS_PATH = Path(__file__).parent / "datasets" / "support_questions.csv"


def _rubric_criteria_json() -> list[dict]:
    rubric = default_support_rubric()
    return [
        {
            "name": criterion.name,
            "label": criterion.label,
            "weight": float(criterion.weight),
            "description": criterion.description,
            "level_descriptions": {str(level): text for level, text in criterion.level_descriptions.items()},
        }
        for criterion in rubric.criteria
    ]


async def _seed_dataset(session, owner_id) -> None:
    existing = await session.scalar(select(Dataset).where(Dataset.name == _DATASET_NAME))
    if existing is not None:
        return

    dataset = Dataset(owner_id=owner_id, name=_DATASET_NAME, description="", source_format=SourceFormat.CSV, is_golden=False)
    session.add(dataset)
    await session.flush()

    with _QUESTIONS_PATH.open(encoding="utf-8", newline="") as handle:
        for position, row in enumerate(csv.DictReader(handle), start=1):
            session.add(
                DatasetItem(
                    dataset_id=dataset.id,
                    position=position,
                    input_prompt=row["input"],
                    expected_output=row.get("expected_output") or None,
                    category=row.get("category") or None,
                    metadata_={},
                )
            )
    print(f"seeded dataset: {_DATASET_NAME}")


async def _seed_rubric(session, owner_id) -> None:
    existing = await session.scalar(select(Rubric).where(Rubric.name == _RUBRIC_NAME))
    if existing is not None:
        return

    session.add(
        Rubric(
            owner_id=owner_id,
            name=_RUBRIC_NAME,
            criteria=_rubric_criteria_json(),
            scale_min=1,
            scale_max=5,
            judge_instructions=_RUBRIC_INSTRUCTIONS,
            version=1,
            is_frozen=False,
        )
    )
    print(f"seeded rubric: {_RUBRIC_NAME}")


async def seed_default_data(session) -> None:
    """Insert the default demo dataset and rubric, owned by the earliest-registered user."""
    owner = await session.scalar(select(User).order_by(User.created_at.asc()).limit(1))
    if owner is None:
        print("seed_default_data: no users yet, skipping dataset/rubric seed.")
        return

    await _seed_dataset(session, owner.id)
    await _seed_rubric(session, owner.id)
    await session.commit()
