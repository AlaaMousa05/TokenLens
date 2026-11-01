from __future__ import annotations

import csv
import io
import json
import uuid
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import Dataset, DatasetItem, Run, SourceFormat

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_DATASET_ITEMS = 1000


class FileValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("Invalid upload file.")


class DatasetInUseError(Exception):
    pass


class DatasetLimitError(Exception):
    pass


@dataclass
class ParsedQuestion:
    input_text: str
    expected_output: str | None


def _normalize_description(description: str | None) -> str:
    return (description or "").strip()


def _normalize_expected_output(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized if normalized != "" else None


def _normalize_required_input(value: str | None) -> str:
    normalized = (value or "").strip()
    if normalized == "":
        raise ValueError("input is required")
    return normalized


async def create_prompt_dataset(
    session: AsyncSession,
    owner_id: uuid.UUID,
    name: str,
    description: str | None,
    input_text: str,
    expected_output: str | None,
) -> tuple[Dataset, DatasetItem]:
    dataset = Dataset(
        owner_id=owner_id,
        name=name.strip(),
        description=_normalize_description(description),
        source_format=SourceFormat.PROMPT,
        is_golden=False,
    )
    session.add(dataset)
    await session.flush()

    item = DatasetItem(
        dataset_id=dataset.id,
        position=1,
        input_prompt=_normalize_required_input(input_text),
        expected_output=_normalize_expected_output(expected_output),
        metadata_={},
    )
    session.add(item)
    await session.commit()
    await session.refresh(dataset)
    await session.refresh(item)
    return dataset, item


def parse_uploaded_questions(filename: str | None, content: bytes) -> tuple[SourceFormat, list[ParsedQuestion]]:
    if len(content) == 0:
        raise FileValidationError(["File is empty."])
    if len(content) > MAX_UPLOAD_BYTES:
        raise FileValidationError([f"File size exceeds {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit."])

    lower_name = (filename or "").lower()
    if lower_name.endswith(".csv"):
        return SourceFormat.CSV, _parse_csv_questions(content)
    if lower_name.endswith(".jsonl"):
        return SourceFormat.JSONL, _parse_jsonl_questions(content)

    raise FileValidationError(["Only .csv or .jsonl files are supported."])


def _parse_csv_questions(content: bytes) -> list[ParsedQuestion]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise FileValidationError(["CSV must be UTF-8 encoded."]) from exc
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise FileValidationError(["CSV must include a header row."])

    if "input" not in reader.fieldnames:
        raise FileValidationError(["CSV must include an 'input' column."])

    rows: list[ParsedQuestion] = []
    errors: list[str] = []

    for index, row in enumerate(reader, start=1):
        if index > MAX_DATASET_ITEMS:
            errors.append(f"Row {index}: row limit exceeded ({MAX_DATASET_ITEMS} max).")
            continue
        try:
            input_text = _normalize_required_input(row.get("input"))
        except ValueError:
            errors.append(f"Row {index}: input is required.")
            continue

        expected_output = _normalize_expected_output(row.get("expected_output"))
        rows.append(ParsedQuestion(input_text=input_text, expected_output=expected_output))

    if len(rows) == 0 and not errors:
        errors.append("CSV has no data rows.")

    if errors:
        raise FileValidationError(errors)

    return rows


def _parse_jsonl_questions(content: bytes) -> list[ParsedQuestion]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise FileValidationError(["JSONL must be UTF-8 encoded."]) from exc
    lines = text.splitlines()
    rows: list[ParsedQuestion] = []
    errors: list[str] = []

    for index, line in enumerate(lines, start=1):
        if line.strip() == "":
            errors.append(f"Row {index}: empty line is not allowed.")
            continue
        if len(rows) >= MAX_DATASET_ITEMS:
            errors.append(f"Row {index}: row limit exceeded ({MAX_DATASET_ITEMS} max).")
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            errors.append(f"Row {index}: invalid JSON.")
            continue

        if not isinstance(data, dict):
            errors.append(f"Row {index}: each line must be a JSON object.")
            continue

        try:
            input_text = _normalize_required_input(data.get("input"))
        except ValueError:
            errors.append(f"Row {index}: input is required.")
            continue

        expected_output = _normalize_expected_output(data.get("expected_output"))
        rows.append(ParsedQuestion(input_text=input_text, expected_output=expected_output))

    if len(rows) == 0 and not errors:
        errors.append("JSONL has no rows.")

    if errors:
        raise FileValidationError(errors)

    return rows


async def create_uploaded_dataset(
    session: AsyncSession,
    owner_id: uuid.UUID,
    name: str,
    description: str | None,
    source_format: SourceFormat,
    questions: list[ParsedQuestion],
) -> Dataset:
    dataset = Dataset(
        owner_id=owner_id,
        name=name.strip(),
        description=_normalize_description(description),
        source_format=source_format,
        is_golden=False,
    )
    session.add(dataset)
    await session.flush()

    for position, question in enumerate(questions, start=1):
        session.add(
            DatasetItem(
                dataset_id=dataset.id,
                position=position,
                input_prompt=question.input_text,
                expected_output=question.expected_output,
                metadata_={},
            )
        )

    await session.commit()
    await session.refresh(dataset)
    return dataset


async def list_user_datasets(
    session: AsyncSession,
    owner_id: uuid.UUID,
    page: int,
    size: int,
) -> tuple[list[tuple[Dataset, int]], int]:
    total = await session.scalar(select(func.count()).select_from(Dataset).where(Dataset.owner_id == owner_id)) or 0
    offset = (page - 1) * size

    query = (
        select(Dataset, func.count(DatasetItem.id))
        .outerjoin(DatasetItem, DatasetItem.dataset_id == Dataset.id)
        .where(Dataset.owner_id == owner_id)
        .group_by(Dataset.id)
        .order_by(Dataset.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    rows = await session.execute(query)
    return [(dataset, item_count) for dataset, item_count in rows.all()], total


async def get_user_dataset(
    session: AsyncSession,
    owner_id: uuid.UUID,
    dataset_id: uuid.UUID,
) -> tuple[Dataset, int] | None:
    query = (
        select(Dataset, func.count(DatasetItem.id))
        .outerjoin(DatasetItem, DatasetItem.dataset_id == Dataset.id)
        .where(Dataset.owner_id == owner_id, Dataset.id == dataset_id)
        .group_by(Dataset.id)
    )
    row = (await session.execute(query)).first()
    if row is None:
        return None
    return row[0], row[1]


async def update_user_dataset(
    session: AsyncSession,
    dataset: Dataset,
    updates: dict,
) -> Dataset:
    if "name" in updates and updates["name"] is not None:
        dataset.name = updates["name"].strip()
    if "description" in updates:
        dataset.description = _normalize_description(updates["description"])
    if "is_golden" in updates and updates["is_golden"] is not None:
        dataset.is_golden = updates["is_golden"]

    await session.commit()
    await session.refresh(dataset)
    return dataset


async def delete_user_dataset(session: AsyncSession, dataset: Dataset) -> None:
    run_exists = await session.scalar(select(func.count()).select_from(Run).where(Run.dataset_id == dataset.id)) or 0
    if run_exists > 0:
        raise DatasetInUseError("Dataset has been used in experiments and cannot be deleted.")

    await session.execute(delete(DatasetItem).where(DatasetItem.dataset_id == dataset.id))
    await session.delete(dataset)
    await session.commit()


async def list_dataset_items(
    session: AsyncSession,
    dataset_id: uuid.UUID,
    page: int,
    size: int,
) -> tuple[list[DatasetItem], int]:
    total = (
        await session.scalar(select(func.count()).select_from(DatasetItem).where(DatasetItem.dataset_id == dataset_id))
        or 0
    )
    offset = (page - 1) * size
    rows = await session.execute(
        select(DatasetItem)
        .where(DatasetItem.dataset_id == dataset_id)
        .order_by(DatasetItem.position.asc())
        .offset(offset)
        .limit(size)
    )
    return list(rows.scalars().all()), total


async def create_dataset_item(
    session: AsyncSession,
    dataset_id: uuid.UUID,
    input_text: str,
    expected_output: str | None,
) -> DatasetItem:
    count = (
        await session.scalar(select(func.count()).select_from(DatasetItem).where(DatasetItem.dataset_id == dataset_id))
        or 0
    )
    if count >= MAX_DATASET_ITEMS:
        raise DatasetLimitError(f"Dataset item limit reached ({MAX_DATASET_ITEMS} max).")

    max_position = await session.scalar(
        select(func.max(DatasetItem.position)).where(DatasetItem.dataset_id == dataset_id)
    )
    item = DatasetItem(
        dataset_id=dataset_id,
        position=(max_position or 0) + 1,
        input_prompt=_normalize_required_input(input_text),
        expected_output=_normalize_expected_output(expected_output),
        metadata_={},
    )
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


async def get_dataset_item(
    session: AsyncSession,
    dataset_id: uuid.UUID,
    item_id: uuid.UUID,
) -> DatasetItem | None:
    row = await session.execute(
        select(DatasetItem).where(DatasetItem.dataset_id == dataset_id, DatasetItem.id == item_id)
    )
    return row.scalar_one_or_none()


async def update_dataset_item(
    session: AsyncSession,
    item: DatasetItem,
    updates: dict,
) -> DatasetItem:
    if "input" in updates:
        item.input_prompt = _normalize_required_input(updates["input"])
    if "expected_output" in updates:
        item.expected_output = _normalize_expected_output(updates["expected_output"])

    await session.commit()
    await session.refresh(item)
    return item


async def delete_dataset_item(session: AsyncSession, item: DatasetItem) -> None:
    await session.delete(item)
    await session.commit()
