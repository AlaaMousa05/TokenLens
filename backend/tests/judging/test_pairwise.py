from evaluation.judging.judge import Judge
from evaluation.judging.rubric import default_support_rubric
from evaluation.judging.verdict import JudgmentStatus
from tests.judging.conftest import StubJudgeClient, make_judge_spec, pairwise_json

_RUBRIC = default_support_rubric()


def _judge(outputs):
    client = StubJudgeClient(outputs)
    return Judge(client, make_judge_spec(), _RUBRIC), client


async def _compare(judge):
    return await judge.compare_pair(policy="P", question="Q", reference="R", answer_a="Alpha answer", answer_b="Beta answer")


async def test_pairwise_runs_two_calls_with_the_answers_exchanged() -> None:
    judge, client = _judge([pairwise_json("A"), pairwise_json("A")])

    await _compare(judge)

    assert len(client.calls) == 2
    first, second = client.calls[0]["prompt"], client.calls[1]["prompt"]
    assert "ANSWER A:\nAlpha answer" in first and "ANSWER B:\nBeta answer" in first
    assert "ANSWER A:\nBeta answer" in second and "ANSWER B:\nAlpha answer" in second


async def test_consistent_winner_survives_the_swap() -> None:
    judge, _ = _judge([pairwise_json("A"), pairwise_json("B")])

    result = await _compare(judge)

    assert result.status is JudgmentStatus.ok
    assert result.verdict_survives_swap is True
    assert result.shows_position_bias is False


async def test_same_position_winning_twice_is_flagged_as_position_bias() -> None:
    judge, _ = _judge([pairwise_json("A"), pairwise_json("A")])

    result = await _compare(judge)

    assert result.verdict_survives_swap is False
    assert result.shows_position_bias is True
