"""Parses the judge's reply into a validated verdict, or an error naming what was wrong.

The error string feeds the single retry, so it must say specifically what failed.
"""

import json

from pydantic import ValidationError

from evaluation.judging.rubric import Rubric
from evaluation.judging.verdict import PairwiseVerdict, Verdict


def parse_scoring_verdict(text: str, rubric: Rubric) -> tuple[Verdict | None, str | None]:
    """Return (verdict, None) on success, or (None, reason) naming the first problem found.

    The wire format is flat — one key per criterion plus 'overall_note' — so the
    judge cannot misfile 'overall_note' inside a 'scores' object.
    """
    payload, error = _load_json(text)
    if error is not None:
        return None, error
    if not isinstance(payload.get("overall_note"), str):
        return None, "reply is missing a top-level string 'overall_note'."
    scores = {key: value for key, value in payload.items() if key != "overall_note"}
    expected = {criterion.name for criterion in rubric.criteria}
    if set(scores) != expected:
        return None, f"reply must have one entry per criterion {sorted(expected)} plus 'overall_note'; got {sorted(scores)}."
    try:
        verdict = Verdict(scores=scores, overall_note=payload["overall_note"])
    except ValidationError as exc:
        return None, f"a criterion entry did not match {{score, rationale}}: {_first_error(exc)}."
    return verdict, None


def parse_pairwise_verdict(text: str) -> tuple[PairwiseVerdict | None, str | None]:
    """Return (verdict, None) on success, or (None, reason) naming the first problem found."""
    payload, error = _load_json(text)
    if error is not None:
        return None, error
    try:
        return PairwiseVerdict.model_validate(payload), None
    except ValidationError as exc:
        return None, f"JSON did not match the comparison schema: {_first_error(exc)}."


def _load_json(text: str) -> tuple[dict | None, str | None]:
    try:
        payload = json.loads(_strip_code_fence(text))
    except json.JSONDecodeError as exc:
        return None, f"reply was not valid JSON: {exc.msg}."
    if not isinstance(payload, dict):
        return None, "reply was valid JSON but not a JSON object."
    return payload, None


def _strip_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.split("\n", 1)[-1]
        if stripped.endswith("```"):
            stripped = stripped.rsplit("```", 1)[0]
    return stripped.strip()


def _first_error(exc: ValidationError) -> str:
    error = exc.errors()[0]
    location = ".".join(str(part) for part in error["loc"]) or "(root)"
    return f"{location}: {error['msg']}"
