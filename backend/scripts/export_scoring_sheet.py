"""Export a blind scoring sheet from a saved run, plus the judge's key for later comparison.

The CSV has empty criterion columns, randomised order and no model identity, so it
can be scored by hand blind. No API calls.

    python -m scripts.export_scoring_sheet [run.json] [seed]
"""

import csv
import json
import sys
from pathlib import Path

from evaluation.judging.rubric import default_support_rubric
from evaluation.measurement.human_agreement import build_scoring_sheet
from evaluation.measurement.persistence import load_run
from scripts._harness import RUNS_DIR

_DEFAULT_SEED = 1


def main() -> None:
    run_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RUNS_DIR / "latest_run.json"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else _DEFAULT_SEED
    criteria = [criterion.name for criterion in default_support_rubric().criteria]

    rows, judge_scores = build_scoring_sheet(load_run(run_path), seed=seed)

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    sheet_path = RUNS_DIR / "scoring_sheet.csv"
    with sheet_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["sheet_id", "question", "candidate_answer", *criteria])
        for row in rows:
            writer.writerow([row.sheet_id, row.question, row.candidate_answer, *([""] * len(criteria))])

    key_path = RUNS_DIR / "judge_key.json"
    key_path.write_text(json.dumps({str(sid): scores for sid, scores in judge_scores.items()}), encoding="utf-8")

    print(f"Wrote {len(rows)} blind rows to {sheet_path}")
    print(f"Wrote judge key to {key_path}")
    print(f"Fill the criterion columns ({', '.join(criteria)}) with 1-5, then run scripts.score_agreement.")


if __name__ == "__main__":
    main()
