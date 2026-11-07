"""Read a human-filled scoring sheet and report agreement with the judge, per criterion.

No API calls.

    python -m scripts.score_agreement [scoring_sheet.csv] [judge_key.json]
"""

import csv
import json
import sys
from pathlib import Path

from evaluation.judging.rubric import default_support_rubric
from evaluation.measurement.human_agreement import compute_agreement
from scripts._harness import RUNS_DIR


def _read_human_scores(path: Path, criteria: list[str]) -> dict[int, dict[str, int]]:
    human: dict[int, dict[str, int]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            filled = {name: int(row[name]) for name in criteria if row.get(name, "").strip()}
            if len(filled) == len(criteria):
                human[int(row["sheet_id"])] = filled
    return human


def main() -> None:
    sheet_path = Path(sys.argv[1]) if len(sys.argv) > 1 else RUNS_DIR / "scoring_sheet.csv"
    key_path = Path(sys.argv[2]) if len(sys.argv) > 2 else RUNS_DIR / "judge_key.json"
    criteria = [criterion.name for criterion in default_support_rubric().criteria]

    judge_scores = {int(sid): scores for sid, scores in json.loads(key_path.read_text(encoding="utf-8")).items()}
    human_scores = _read_human_scores(sheet_path, criteria)
    if not human_scores:
        print("No fully-scored rows found in the sheet; fill every criterion column with 1-5.")
        return

    print(f"=== Judge/human agreement over {len(set(judge_scores) & set(human_scores))} rows ===")
    for agreement in compute_agreement(judge_scores, human_scores, criteria):
        print(
            f"  {agreement.criterion:<16} exact={agreement.exact_rate}  "
            f"within_1={agreement.within_one_rate}  over_1={agreement.over_one_rate}  (n={agreement.compared})"
        )


if __name__ == "__main__":
    main()
