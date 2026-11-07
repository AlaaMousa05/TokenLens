import json
from datetime import datetime, timezone
from decimal import Decimal

from evaluation.contracts import CallStatus, CompletionOutcome, ModelClient, ModelResponse, ModelSpec, PriceSnapshot

_SNAPSHOT = PriceSnapshot(
    input_price_per_mtok=Decimal("0.71"),
    output_price_per_mtok=Decimal("0.71"),
    cached_input_price_per_mtok=None,
    captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)


def make_judge_spec(name: str = "Llama-3.3-70B-Instruct", accepts_custom_temperature: bool = True) -> ModelSpec:
    return ModelSpec(
        provider="azure_ai_foundry",
        model_name=name,
        display_name=name,
        context_window=128000,
        input_price_per_mtok=Decimal("0.71"),
        output_price_per_mtok=Decimal("0.71"),
        pricing_notes="test fixture",
        is_active=True,
        is_judge_eligible=True,
        accepts_custom_temperature=accepts_custom_temperature,
    )


def scoring_json(policy_fidelity: int, completeness: int, honesty: int, conciseness: int) -> str:
    return json.dumps(
        {
            "policy_fidelity": {"score": policy_fidelity, "rationale": "r"},
            "completeness": {"score": completeness, "rationale": "r"},
            "honesty": {"score": honesty, "rationale": "r"},
            "conciseness": {"score": conciseness, "rationale": "r"},
            "overall_note": "summary",
        }
    )


def pairwise_json(overall: str) -> str:
    return json.dumps({"overall": overall, "rationale": "r"})


class StubJudgeClient(ModelClient):
    """Returns preset output text per call, recording every call's prompts and settings."""

    def __init__(self, outputs: list[str], status: CallStatus = CallStatus.ok, error_message: str | None = None) -> None:
        self._outputs = outputs
        self._status = status
        self._error_message = error_message
        self.calls: list[dict] = []

    async def complete(self, spec, prompt, system_prompt, temperature, max_output_tokens) -> ModelResponse:
        self.calls.append(
            {
                "spec": spec,
                "prompt": prompt,
                "system_prompt": system_prompt,
                "temperature": temperature,
                "max_output_tokens": max_output_tokens,
            }
        )
        index = min(len(self.calls) - 1, len(self._outputs) - 1)
        outcome = CompletionOutcome.normal if self._status is CallStatus.ok else None
        return ModelResponse(
            output_text=self._outputs[index] if self._outputs else "",
            latency_ms=1,
            attempts=1,
            status=self._status,
            completion_outcome=outcome,
            error_message=self._error_message,
            tokens_estimated=False,
            prices_snapshot=_SNAPSHOT,
        )
