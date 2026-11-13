"""Run the whole dataset against all compared models with N repeats, judged, caching off.

Persists the raw run to JSON and prints the manifest plus per-model aggregation.

    python -m scripts.run_full [repeats] [out.json]
"""

import asyncio
import sys
from pathlib import Path

from evaluation.judging import Judge, default_support_rubric, ensure_judge_not_judged
from evaluation.measurement.aggregation import aggregate
from evaluation.measurement.full_run import run_dataset
from evaluation.measurement.persistence import save_run
from evaluation.measurement.records import FullRun, scored_answers
from evaluation.measurement.usage import UsageRecorder
from evaluation.registry import get_compared_models, get_default_judge
from scripts._harness import DATASET_PATH, RUNS_DIR, load_policy, load_rows, new_execution

_DEFAULT_REPEATS = 3


def print_manifest(run: FullRun) -> None:
    manifest = run.manifest
    print("=== Run manifest ===")
    print(f"  dataset_version: {manifest.dataset_version}")
    print(f"  rubric:          {manifest.rubric_name} v{manifest.rubric_version}")
    print(f"  judge:           {manifest.judge_model}")
    print(f"  repeats:         {manifest.repeats}")
    print(f"  timestamp:       {manifest.created_at.isoformat()}")
    print(f"  total cost:      ${manifest.total_cost}")
    print(f"  total tokens:    {manifest.total_tokens}")


def print_aggregation(run: FullRun) -> None:
    aggregates = aggregate(scored_answers(run))
    for name, model in aggregates.items():
        print(f"\n{name}  overall {model.overall}")
        for category, stat in model.per_category.items():
            print(f"  [{category:<13}] total {stat}")
        for criterion, stat in model.per_criterion.items():
            print(f"  {criterion:<16} {stat}")


async def main() -> None:
    repeats = int(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_REPEATS
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else RUNS_DIR / "latest_run.json"

    candidate_models = get_compared_models()
    judge_spec = get_default_judge()
    ensure_judge_not_judged(judge_spec, candidate_models)

    execution, _ = new_execution(use_cache=False)
    recorder = UsageRecorder(execution.select(use_cache=False))
    judge = Judge(recorder, judge_spec, default_support_rubric())

    run = await run_dataset(
        recorder=recorder,
        judge=judge,
        judge_model=judge_spec.model_name,
        candidate_models=candidate_models,
        policy=load_policy(),
        rows=load_rows(),
        repeats=repeats,
        rubric=default_support_rubric(),
        dataset_path=DATASET_PATH,
    )
    save_run(run, out_path)
    print_manifest(run)
    print_aggregation(run)
    print(f"\nSaved run to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
