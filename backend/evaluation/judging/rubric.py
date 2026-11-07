"""The scoring rubric as data: criteria, weights, and a concrete 1-5 scale.

A rubric is edited by admins and lives in the database; this layer models it
only. It is immutable — a revision returns a new version rather than mutating,
so a frozen rubric a golden run was scored against can never change underneath
those scores.
"""

from decimal import ROUND_HALF_UP, Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

_SCALE_LEVELS = frozenset({1, 2, 3, 4, 5})
_TWO_PLACES = Decimal("0.01")


class Criterion(BaseModel):
    """One scored dimension, with a weight and a concrete statement per 1-5 level."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Stable key the judge scores against, e.g. 'policy_fidelity'.")
    label: str = Field(description="Human-readable name for the UI.")
    weight: Decimal = Field(description="Share of the weighted total; weights across a rubric sum to 1.")
    description: str = Field(description="What this criterion measures.")
    level_descriptions: dict[int, str] = Field(
        description="Concrete meaning of each score 1-5, so the judge does not invent its own scale."
    )

    @model_validator(mode="after")
    def _levels_cover_the_scale(self) -> "Criterion":
        if set(self.level_descriptions) != _SCALE_LEVELS:
            raise ValueError(f"Criterion '{self.name}' must describe exactly levels 1-5.")
        return self


class Rubric(BaseModel):
    """A versioned set of weighted criteria. Immutable; revise() yields the next version."""

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="Rubric identity, shared across its versions.")
    version: int = Field(description="Increments on every revision.")
    is_frozen: bool = Field(description="Locked for golden runs; editing produces a new version, never a mutation.")
    criteria: tuple[Criterion, ...] = Field(description="The scored dimensions.")

    @model_validator(mode="after")
    def _weights_sum_to_one(self) -> "Rubric":
        total = sum((criterion.weight for criterion in self.criteria), Decimal("0"))
        if total != Decimal("1"):
            raise ValueError(f"Criterion weights must sum to 1, got {total}.")
        return self

    def weighted_total(self, scores: dict[str, int]) -> Decimal:
        """Deterministic weighted mean of per-criterion scores; the judge never computes this."""
        missing = {criterion.name for criterion in self.criteria} - set(scores)
        if missing:
            raise ValueError(f"Scores missing for criteria: {sorted(missing)}.")
        total = sum((criterion.weight * scores[criterion.name] for criterion in self.criteria), Decimal("0"))
        return total.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)

    def freeze(self) -> "Rubric":
        """Return a locked copy of this rubric."""
        return Rubric(name=self.name, version=self.version, is_frozen=True, criteria=self.criteria)

    def revise(self, criteria: tuple[Criterion, ...]) -> "Rubric":
        """Return the next version with new criteria, unfrozen and revalidated; leaves this one untouched."""
        return Rubric(name=self.name, version=self.version + 1, is_frozen=False, criteria=criteria)


def default_support_rubric() -> Rubric:
    """The built-in template for scoring customer-support answers against a product policy."""
    return Rubric(
        name="customer_support_default",
        version=1,
        is_frozen=True,
        criteria=(
            Criterion(
                name="policy_fidelity",
                label="Policy fidelity",
                weight=Decimal("0.40"),
                description="The answer follows the stated policy and applies only rules the policy contains.",
                level_descriptions={
                    1: "Contradicts the policy or applies a rule the policy does not contain.",
                    2: "Cites the policy but gets the governing rule backwards or materially misstates it.",
                    3: "The main rule is right but a detail is misapplied.",
                    4: "Correct on the governing rule with at most a minor imprecision.",
                    5: "Applies exactly the rules the policy states, no more and no less.",
                },
            ),
            Criterion(
                name="completeness",
                label="Completeness",
                weight=Decimal("0.25"),
                description=(
                    "Every rule the question actually requires is addressed, including where two rules must "
                    "combine. Judged only against what this question asks: omitting detail the question did not "
                    "request is not a loss, and adding unrequested detail is never a completeness gain."
                ),
                level_descriptions={
                    1: "Omits the rule the answer to this question depends on.",
                    2: "Addresses one rule the question needs but omits another it requires, such as a second rule that must combine.",
                    3: "Covers the main required rule but misses a secondary condition this question's answer depends on.",
                    4: "Addresses every rule this question requires; a minor required qualifier is left implicit.",
                    5: "Addresses every rule and condition this question requires, including any interaction between them.",
                },
            ),
            Criterion(
                name="honesty",
                label="Honesty",
                weight=Decimal("0.20"),
                description="Says the policy does not cover a case instead of inventing, and corrects a false premise.",
                level_descriptions={
                    1: "Invents a rule, answers an uncovered case confidently, or accepts a false premise.",
                    2: "Partly fabricates, or leaves a false premise in the question uncorrected.",
                    3: "Hedges without stating the policy is silent, or corrects the premise only weakly.",
                    4: "States the limit or corrects the premise, with slightly unclear wording.",
                    5: "Clearly flags when the policy is silent and explicitly corrects any false premise.",
                },
            ),
            Criterion(
                name="conciseness",
                label="Conciseness",
                weight=Decimal("0.15"),
                description="Direct, with no padding or restated boilerplate.",
                level_descriptions={
                    1: "Buried in padding, restated boilerplate, or long digressions.",
                    2: "Noticeably verbose; the answer is there but surrounded by filler.",
                    3: "Somewhat wordy but readable.",
                    4: "Mostly tight with minor redundancy.",
                    5: "Direct and minimal; every sentence earns its place.",
                },
            ),
        ),
    )
