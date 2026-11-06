from decimal import Decimal

import pytest
from pydantic import ValidationError

from evaluation.judging.rubric import Criterion, default_support_rubric


def test_weighted_total_combines_scores_by_weight() -> None:
    rubric = default_support_rubric()

    total = rubric.weighted_total(
        {"policy_fidelity": 5, "completeness": 4, "honesty": 3, "conciseness": 2}
    )

    assert total == Decimal("3.90")


def test_weighted_total_requires_every_criterion() -> None:
    rubric = default_support_rubric()

    with pytest.raises(ValueError):
        rubric.weighted_total({"policy_fidelity": 5})


def test_weights_must_sum_to_one() -> None:
    rubric = default_support_rubric()
    lopsided = tuple(c.model_copy(update={"weight": Decimal("0.10")}) for c in rubric.criteria)

    with pytest.raises(ValidationError):
        rubric.revise(lopsided)


def test_criterion_requires_all_five_levels() -> None:
    with pytest.raises(ValidationError):
        Criterion(
            name="x",
            label="X",
            weight=Decimal("1.00"),
            description="d",
            level_descriptions={1: "a", 2: "b", 3: "c"},
        )


def test_revise_creates_a_new_unfrozen_version_leaving_the_original_frozen() -> None:
    original = default_support_rubric()
    assert original.is_frozen and original.version == 1

    revised = original.revise(original.criteria)

    assert revised.version == 2
    assert revised.is_frozen is False
    assert original.is_frozen is True
    assert original.version == 1
