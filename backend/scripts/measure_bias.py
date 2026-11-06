"""Position and length bias over a saved run (reuses its answers; only judge calls are made).

Position bias: compare every model pair on every row twice with the order swapped.
Length bias: compare equally-scored answers that differ in length; report how often
the longer wins.

    python -m scripts.measure_bias [run.json]
"""

import asyncio
import sys
from itertools import combinations
from pathlib import Path

from evaluation.judging import Judge, default_support_rubric
from evaluation.measurement.length_bias import build_length_pairs, longer_won, summarize_length_bias
from evaluation.measurement.persistence import load_run
from evaluation.measurement.position_bias import position_bias
from evaluation.measurement.records import FullRun, scored_answers
from evaluation.measurement.usage import UsageRecorder
from evaluation.registry import get_default_judge
from scripts._harness import RUNS_DIR, load_policy, load_rows, new_execution


def _repeat_zero(run: FullRun) -> FullRun:
    return FullRun(manifest=run.manifest, records=[record for record in run.records if record.repeat == 0])


async def main() -> None:
    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RUNS_DIR / "latest_run.json"
    run = _repeat_zero(load_run(run_path))
    policy = load_policy()
    rows = {row.row_id: row for row in load_rows()}
    answer = {(record.model_name, record.row_id): record.candidate_answer for record in run.records}
    models = sorted({record.model_name for record in run.records})
    row_ids = sorted({record.row_id for record in run.records})

    execution, _ = new_execution(use_cache=False)
    recorder = UsageRecorder(execution.select(use_cache=False))
    judge = Judge(recorder, get_default_judge(), default_support_rubric())

    outcomes = []
    for row_id in row_ids:
        row = rows[row_id]
        for first, second in combinations(models, 2):
            outcomes.append(
                await judge.compare_pair(policy, row.question, row.reference, answer[(first, row_id)], answer[(second, row_id)])
            )
    position = position_bias(outcomes)
    print("=== Position bias ===")
    print(f"  comparisons={position.comparisons}  flips={position.flips}  flip_rate={position.flip_rate}")

    pairs, selection = build_length_pairs(scored_answers(run))
    interpretations = []
    for pair in pairs:
        row = rows[pair.row_id]
        longer_text = answer[(pair.longer.model_name, pair.row_id)]
        shorter_text = answer[(pair.shorter.model_name, pair.row_id)]
        interpretations.append(longer_won(await judge.compare_pair(policy, row.question, row.reference, longer_text, shorter_text)))
    length = summarize_length_bias(interpretations, selection)
    print("\n=== Length bias ===")
    print(f"  selection: {length.selection}")
    underpowered = "  underpowered" if length.underpowered else ""
    print(
        f"  pairs={len(pairs)}  decisive={length.decisive}  longer_preferred={length.longer_preferred}  "
        f"rate={length.longer_preference_rate}{underpowered}"
    )
    print(f"\njudge calls cost ${recorder.total_cost}  tokens {recorder.total_tokens}")


if __name__ == "__main__":
    asyncio.run(main())
