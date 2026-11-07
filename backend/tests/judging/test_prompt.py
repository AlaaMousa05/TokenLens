from evaluation.judging.prompt import render_pairwise_prompt, render_scoring_prompt
from evaluation.judging.rubric import default_support_rubric

_MODEL_NAME = "gpt-4.1"


def test_scoring_prompt_includes_the_inputs_but_not_the_model_identity() -> None:
    system, user = render_scoring_prompt(
        default_support_rubric(),
        policy="POLICY TEXT",
        question="QUESTION TEXT",
        reference="REFERENCE TEXT",
        candidate="The refund window is 14 days.",
    )

    combined = system + user
    assert "POLICY TEXT" in user
    assert "QUESTION TEXT" in user
    assert "REFERENCE TEXT" in user
    assert "The refund window is 14 days." in user
    assert "policy_fidelity" in system
    assert _MODEL_NAME not in combined
    assert "azure" not in combined.lower()


def test_pairwise_prompt_labels_answers_a_and_b_without_identity() -> None:
    system, user = render_pairwise_prompt(
        default_support_rubric(),
        policy="P",
        question="Q",
        reference="R",
        answer_a="first answer",
        answer_b="second answer",
    )

    assert "ANSWER A:" in user and "first answer" in user
    assert "ANSWER B:" in user and "second answer" in user
    assert _MODEL_NAME not in system + user
