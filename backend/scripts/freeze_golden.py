"""Freeze a saved run as a golden baseline for later regression checks. No API calls.

    python -m scripts.freeze_golden [run.json] [golden.json]
"""

import sys
from pathlib import Path

from evaluation.measurement.aggregation import aggregate
from evaluation.measurement.persistence import load_run
from evaluation.measurement.records import scored_answers
from evaluation.regression.golden import freeze_golden, save_golden
from scripts._harness import RUNS_DIR


def main() -> None:
    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RUNS_DIR / "latest_run.json"
    golden_path = Path(sys.argv[2]) if len(sys.argv) > 2 else RUNS_DIR / "golden.json"

    run = load_run(run_path)
    golden = freeze_golden(run.manifest, aggregate(scored_answers(run)))
    save_golden(golden, golden_path)
    print(f"Froze golden baseline (dataset {golden.dataset_version}, rubric {golden.rubric_name} v{golden.rubric_version}, "
          f"judge {golden.judge_model}, repeats {golden.repeats}) to {golden_path}")


if __name__ == "__main__":
    main()
