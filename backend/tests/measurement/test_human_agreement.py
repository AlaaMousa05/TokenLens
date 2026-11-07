from decimal import Decimal

from evaluation.measurement.human_agreement import build_scoring_sheet, compute_agreement
from tests.measurement.conftest import make_record, make_run


def test_agreement_per_criterion_including_over_one_point() -> None:
    judge = {1: {"a": 5, "b": 4}, 2: {"a": 3, "b": 5}}
    human = {1: {"a": 5, "b": 5}, 2: {"a": 1, "b": 5}}

    by_criterion = {ag.criterion: ag for ag in compute_agreement(judge, human, ["a", "b"])}

    assert by_criterion["a"].exact_rate == Decimal("0.500")
    assert by_criterion["a"].within_one_rate == Decimal("0.500")
    assert by_criterion["a"].over_one_rate == Decimal("0.500")
    assert by_criterion["b"].within_one_rate == Decimal("1.000")
    assert by_criterion["b"].over_one_rate == Decimal("0.000")


def test_scoring_sheet_is_blind_and_keyed_to_judge_scores() -> None:
    run = make_run(
        [
            make_record("gpt-4.1", 0, "lookup", "Q0", "answer zero", {"a": 5, "b": 4}, "4"),
            make_record("Llama-3.3-70B-Instruct", 1, "uncovered", "Q1", "answer one", {"a": 2, "b": 3}, "2"),
        ]
    )

    rows, judge_scores = build_scoring_sheet(run, seed=7)

    assert len(rows) == 2
    assert set(judge_scores) == {row.sheet_id for row in rows}
    for row in rows:
        assert "gpt-4.1" not in row.candidate_answer and "Llama" not in row.candidate_answer
        assert not hasattr(row, "model_name")
