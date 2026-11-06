"""Hold candidate answers fixed and judge each N times to quantify judge noise.

A single easy lookup answer tends to score the maximum every time, which
measures a floor effect (zero noise) rather than real judge disagreement. This
probes answers from harder categories instead — where the judge has room to
land on different scores — including one from the uncovered category, and
prints which answers were used so the measurement is checkable.

Saves the largest per-answer standard deviation, which the regression
threshold is derived from.

    python -m scripts.measure_variance [judgings] [out.json]
"""

import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path

from evaluation.contracts import CallStatus
from evaluation.judging import Judge, default_support_rubric, ensure_judge_not_judged
from evaluation.judging.verdict import JudgmentStatus
from evaluation.measurement.full_run import DatasetRow
from evaluation.measurement.usage import UsageRecorder
from evaluation.measurement.variance import summarize_variance
from evaluation.registry import get_compared_models, get_default_judge
from scripts._harness import RUNS_DIR, load_policy, load_rows, new_execution

_DEFAULT_JUDGINGS = 10

# Categories chosen for room to disagree, not a guaranteed top score: a
# two-rule combination the candidate may partially miss, and an uncovered
# case as required.
_PROBE_CATEGORIES = ["two_rule", "uncovered"]


def _probe_rows(rows: list[DatasetRow]) -> list[DatasetRow]:
    return [next(row for row in rows if row.category == category) for category in _PROBE_CATEGORIES]


async def _probe_one(judge: Judge, recorder: UsageRecorder, policy: str, row: DatasetRow, judgings: int) -> Decimal | None:
    answer = await recorder.complete(get_compared_models()[0], row.question, policy, 0.0, 512)
    if answer.status is not CallStatus.ok:
        print(f"[{row.category}] candidate generation failed: {answer.error_message}")
        return None

    print(f"\nProbe answer [{row.category}] Q: {row.question}")
    print(f"  A: {answer.output_text[:200]}")

    totals = []
    for _ in range(judgings):
        judgment = await judge.score(policy, row.question, row.reference, answer.output_text)
        if judgment.status is JudgmentStatus.ok:
            totals.append(judgment.weighted_total)

    if len(totals) < 2:
        print(f"  only {len(totals)} successful judgment(s) of {judgings}; cannot measure variance for this answer.")
        return None

    summary = summarize_variance(totals)
    print(f"  judged {len(totals)}x (of {judgings}): {summary.stat}")
    print(f"  min={summary.minimum}  max={summary.maximum}  spread={summary.spread}")
    return summary.stat.stddev


async def main() -> None:
    judgings = int(sys.argv[1]) if len(sys.argv) > 1 else _DEFAULT_JUDGINGS
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else RUNS_DIR / "variance.json"

    candidate_model = get_compared_models()[0]
    judge_spec = get_default_judge()
    ensure_judge_not_judged(judge_spec, [candidate_model])
    policy = load_policy()
    probe_rows = _probe_rows(load_rows())

    execution, _ = new_execution(use_cache=False)
    recorder = UsageRecorder(execution.select(use_cache=False))
    judge = Judge(recorder, judge_spec, default_support_rubric())

    stddevs = [stddev for row in probe_rows if (stddev := await _probe_one(judge, recorder, policy, row, judgings)) is not None]

    if not stddevs:
        print("\nNo probe answer produced enough judgments to measure variance.")
        return

    judge_noise = max(stddevs)
    print(f"\nUsing the largest per-answer stddev across {len(stddevs)} probe(s) as judge noise: {judge_noise}")
    print(f"total cost ${recorder.total_cost}  tokens {recorder.total_tokens}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"judge_noise_stddev": str(judge_noise)}), encoding="utf-8")
    print(f"Saved judge noise stddev to {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
