"""Renders the judge prompt from a rubric.

The judge is shown the policy, question, reference answer and candidate
answer(s) and nothing that identifies which model produced them — not in a
label, not in metadata.
"""

from evaluation.judging.rubric import Rubric

_SCORING_INSTRUCTIONS = (
    "You are grading one answer to a customer-support question against a product policy. "
    "You are given no information about which system produced the answer; judge only the text. "
    "Score each criterion independently on its 1-5 scale, each with a one-sentence rationale. "
    "Do not compute or report a total. Reply with ONLY the JSON described below and no other text."
)

_PAIRWISE_INSTRUCTIONS = (
    "You are comparing two answers, A and B, to a customer-support question against a product policy. "
    "You are given no information about which system produced either answer; judge only the text. "
    "Weigh the criteria below and decide which answer is better overall, or 'tie'. "
    "Reply with ONLY the JSON described below and no other text."
)


def render_scoring_prompt(
    rubric: Rubric,
    policy: str,
    question: str,
    reference: str,
    candidate: str,
) -> tuple[str, str]:
    """Build the (system, user) prompt for scoring one candidate answer."""
    system = "\n\n".join([_SCORING_INSTRUCTIONS, _render_criteria(rubric), _scoring_schema(rubric)])
    user = "\n\n".join(
        [
            f"POLICY:\n{policy}",
            f"QUESTION:\n{question}",
            f"REFERENCE ANSWER:\n{reference}",
            f"CANDIDATE ANSWER:\n{candidate}",
        ]
    )
    return system, user


def render_pairwise_prompt(
    rubric: Rubric,
    policy: str,
    question: str,
    reference: str,
    answer_a: str,
    answer_b: str,
) -> tuple[str, str]:
    """Build the (system, user) prompt for comparing answer A against answer B."""
    system = "\n\n".join([_PAIRWISE_INSTRUCTIONS, _render_criteria(rubric), _PAIRWISE_SCHEMA])
    user = "\n\n".join(
        [
            f"POLICY:\n{policy}",
            f"QUESTION:\n{question}",
            f"REFERENCE ANSWER:\n{reference}",
            f"ANSWER A:\n{answer_a}",
            f"ANSWER B:\n{answer_b}",
        ]
    )
    return system, user


def _render_criteria(rubric: Rubric) -> str:
    blocks = ["CRITERIA (score each 1-5 using these exact level meanings):"]
    for criterion in rubric.criteria:
        levels = "\n".join(f"  {level}: {text}" for level, text in sorted(criterion.level_descriptions.items()))
        blocks.append(f"{criterion.name} — {criterion.label}: {criterion.description}\n{levels}")
    return "\n\n".join(blocks)


def _scoring_schema(rubric: Rubric) -> str:
    entries = ",\n".join(
        f'  "{criterion.name}": {{"score": <integer 1-5>, "rationale": "<one sentence>"}}'
        for criterion in rubric.criteria
    )
    return (
        "Return ONLY a JSON object with one top-level key per criterion plus "
        '"overall_note", and nothing else:\n'
        "{\n"
        f"{entries},\n"
        '  "overall_note": "<one sentence summary, not a score>"\n'
        "}"
    )


_PAIRWISE_SCHEMA = 'Return ONLY this JSON:\n{"overall": "A" | "B" | "tie", "rationale": "<one sentence>"}'
