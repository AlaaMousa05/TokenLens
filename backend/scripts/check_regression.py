"""Compare a later run against the golden baseline, alerting on drops beyond judge noise.

The threshold is derived from the measured run-to-run variance, not a constant.
No API calls.

    python -m scripts.check_regression [current_run.json] [golden.json] [variance.json]
"""

import json
import sys
from decimal import Decimal
from pathlib import Path

from evaluation.measurement.aggregation import aggregate
from evaluation.measurement.persistence import load_run
from evaluation.measurement.records import scored_answers
from evaluation.regression.compare import compare_to_golden
from evaluation.regression.golden import load_golden
from evaluation.regression.threshold import derive_threshold
from scripts._harness import RUNS_DIR


def main() -> None:
    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RUNS_DIR / "latest_run.json"
    golden_path = Path(sys.argv[2]) if len(sys.argv) > 2 else RUNS_DIR / "golden.json"
    variance_path = Path(sys.argv[3]) if len(sys.argv) > 3 else RUNS_DIR / "variance.json"

    judge_noise = Decimal(json.loads(variance_path.read_text(encoding="utf-8"))["judge_noise_stddev"])
    threshold = derive_threshold(judge_noise)
    golden = load_golden(golden_path)
    current = aggregate(scored_answers(load_run(run_path)))

    print(f"=== Regression check against golden (dataset {golden.dataset_version}, judge {golden.judge_model}) ===")
    print(f"  threshold: {threshold.derivation}")
    alerts = compare_to_golden(golden, current, threshold)
    if not alerts:
        print("  no regressions beyond the judge's noise.")
        return
    for alert in alerts:
        print(
            f"  ALERT {alert.model_name} [{alert.category}]: total {alert.baseline_total} -> {alert.current_total} "
            f"(drop {alert.drop}, > {threshold.value}); worst criterion {alert.worst_criterion} (drop {alert.worst_criterion_drop})"
        )


if __name__ == "__main__":
    main()
