"""Scores dataset rows against one compared model using the real judge.

Samples rows across question categories (not the first N, which are all easy
lookups), runs a compared model to produce candidate answers, has the default
judge score each against the reference, and prints per-row verdicts plus a
per-category summary — because "strong on lookups, collapses on uncovered
cases" is a finding and one average is not. Reads real keys from settings;
judging goes through the execution layer with caching off. Run manually:

    python -m scripts.judge_demo
"""

import asyncio
import csv
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import evaluation.judging as judging_package
from app.config import settings
from evaluation.contracts import CallStatus
from evaluation.execution import InMemoryCache, ProviderConcurrency, RetryPolicy, build_execution_client
from evaluation.execution.caching_client import CacheStats
from evaluation.judging import Judge, default_support_rubric, ensure_judge_not_judged
from evaluation.judging.verdict import Judgment, JudgmentStatus
from evaluation.providers.resolver import resolve_client
from evaluation.registry import get_compared_models, get_default_judge

_DATASETS = Path(judging_package.__file__).parent / "datasets"
_CATEGORY_ORDER = ["lookup", "two_rule", "uncovered", "false_premise", "ambiguous"]
_SAMPLES_PER_CATEGORY = 2
_CANDIDATE_MAX_TOKENS = 256
_CRITERIA = ("policy_fidelity", "completeness", "honesty", "conciseness")


def _load_policy() -> str:
    return (_DATASETS / "support_policy.md").read_text(encoding="utf-8")


def _sample_rows(per_category: int) -> list[dict[str, str]]:
    with (_DATASETS / "support_questions.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    by_category: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_category[row["category"]].append(row)
    return [row for category in _CATEGORY_ORDER for row in by_category[category][:per_category]]


def _build_client():
    execution = build_execution_client(
        resolve=lambda spec: resolve_client(
            spec, google_api_key=settings.google_api_key, azure_api_key=settings.azure_api_key
        ),
        concurrency=ProviderConcurrency(),
        cache_backend=InMemoryCache(),
        cache_stats=CacheStats(),
        retry_policy=RetryPolicy(),
    )
    return execution.select(use_cache=False)


def _mean(values: list[Decimal]) -> Decimal:
    return (sum(values) / len(values)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _print_judgment(category: str, question: str, candidate: str, judgment: Judgment) -> None:
    print(f"\n[{category}] Q: {question}")
    print(f"  candidate: {candidate[:150]}")
    if judgment.status is not JudgmentStatus.ok:
        print(f"  JUDGE FAILED after {judgment.attempts} attempt(s): {judgment.error_message}")
        return
    scores = "  ".join(f"{name}={judgment.verdict.scores[name].score}" for name in _CRITERIA)
    print(f"  {scores}  => total {judgment.weighted_total}")
    print(f"  honesty note: {judgment.verdict.scores['honesty'].rationale}")


def _print_summary(scored: list[tuple[str, Judgment]]) -> None:
    print("\n=== Per-category summary (mean scores) ===")
    header = f"{'category':<14}{'n':>3}{'total':>8}" + "".join(f"{name[:12]:>14}" for name in _CRITERIA)
    print(header)
    for category in _CATEGORY_ORDER:
        judgments = [j for cat, j in scored if cat == category and j.status is JudgmentStatus.ok]
        if not judgments:
            print(f"{category:<14}{0:>3}")
            continue
        total = _mean([j.weighted_total for j in judgments])
        row = f"{category:<14}{len(judgments):>3}{total:>8}"
        for name in _CRITERIA:
            row += f"{_mean([Decimal(j.verdict.scores[name].score) for j in judgments]):>14}"
        print(row)


async def main() -> None:
    policy = _load_policy()
    rows = _sample_rows(_SAMPLES_PER_CATEGORY)
    candidate_model = get_compared_models()[1]
    judge_spec = get_default_judge()
    ensure_judge_not_judged(judge_spec, [candidate_model])

    client = _build_client()
    judge = Judge(client, judge_spec, default_support_rubric())
    print(f"Candidate model: {candidate_model.display_name}   Judge: {judge_spec.display_name}")

    scored: list[tuple[str, Judgment]] = []
    for row in rows:
        question, reference, category = row["input"], row["expected_output"], row["category"]
        answer = await client.complete(candidate_model, question, policy, 0.0, _CANDIDATE_MAX_TOKENS)
        if answer.status is not CallStatus.ok:
            print(f"\n[{category}] Q: {question}\n  candidate call failed: {answer.error_message}")
            continue
        judgment = await judge.score(policy, question, reference, answer.output_text)
        scored.append((category, judgment))
        _print_judgment(category, question, answer.output_text, judgment)

    _print_summary(scored)


if __name__ == "__main__":
    asyncio.run(main())
