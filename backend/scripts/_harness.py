"""Shared wiring for the measurement and regression scripts.

Builds the execution client from real settings keys, loads the support dataset,
and fixes the on-disk locations for run artifacts.
"""

import csv
from pathlib import Path

import evaluation.judging as judging_package
from app.config import settings
from evaluation.execution import InMemoryCache, ProviderConcurrency, RetryPolicy, build_execution_client
from evaluation.execution.caching_client import CacheStats
from evaluation.execution.composition import ExecutionClient
from evaluation.measurement.full_run import DatasetRow
from evaluation.providers.resolver import resolve_client

_DATASETS = Path(judging_package.__file__).parent / "datasets"
DATASET_PATH = _DATASETS / "support_questions.csv"
POLICY_PATH = _DATASETS / "support_policy.md"
RUNS_DIR = Path("runs")


def new_execution(use_cache: bool) -> tuple[ExecutionClient, CacheStats]:
    """A fresh execution client and its cache-stats counter, wired to real API keys."""
    stats = CacheStats()
    execution = build_execution_client(
        resolve=lambda spec: resolve_client(
            spec, google_api_key=settings.google_api_key, azure_api_key=settings.azure_api_key
        ),
        concurrency=ProviderConcurrency(),
        cache_backend=InMemoryCache(),
        cache_stats=stats,
        retry_policy=RetryPolicy(),
    )
    return execution, stats


def load_policy() -> str:
    return POLICY_PATH.read_text(encoding="utf-8")


def load_rows() -> list[DatasetRow]:
    with DATASET_PATH.open(encoding="utf-8", newline="") as handle:
        return [
            DatasetRow(row_id=index, question=row["input"], reference=row["expected_output"], category=row["category"])
            for index, row in enumerate(csv.DictReader(handle))
        ]
