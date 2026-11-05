import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from evaluation.contracts import (
    CallStatus,
    CompletionOutcome,
    ModelClient,
    ModelResponse,
    ModelSpec,
    PriceSnapshot,
)

_SNAPSHOT = PriceSnapshot(
    input_price_per_mtok=Decimal("1.00"),
    output_price_per_mtok=Decimal("2.00"),
    cached_input_price_per_mtok=None,
    captured_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
)


def make_spec(provider: str, model_name: str = "m") -> ModelSpec:
    return ModelSpec(
        provider=provider,
        model_name=model_name,
        display_name=f"{model_name} ({provider})",
        context_window=131072,
        input_price_per_mtok=Decimal("1.00"),
        output_price_per_mtok=Decimal("2.00"),
        pricing_notes="test fixture",
        is_active=True,
    )


def ok_response(input_tokens: int = 10, output_tokens: int = 5) -> ModelResponse:
    return ModelResponse(
        output_text="answer",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=10,
        attempts=1,
        status=CallStatus.ok,
        completion_outcome=CompletionOutcome.normal,
        tokens_estimated=False,
        prices_snapshot=_SNAPSHOT,
    )


def failed_response(error_message: str, retry_after_seconds: float | None = None) -> ModelResponse:
    return ModelResponse(
        output_text="",
        latency_ms=10,
        attempts=1,
        status=CallStatus.failed,
        error_message=error_message,
        retry_after_seconds=retry_after_seconds,
        tokens_estimated=False,
        prices_snapshot=_SNAPSHOT,
    )


def non_normal_response(outcome: CompletionOutcome) -> ModelResponse:
    return ok_response().model_copy(update={"completion_outcome": outcome})


class ScriptedClient(ModelClient):
    """Returns a preset response per attempt, repeating the last; counts calls."""

    def __init__(self, responses: list[ModelResponse]) -> None:
        self._responses = responses
        self.calls = 0

    async def complete(self, spec, prompt, system_prompt, temperature, max_output_tokens) -> ModelResponse:
        index = min(self.calls, len(self._responses) - 1)
        self.calls += 1
        return self._responses[index]


class CountingClient(ModelClient):
    """Returns the same response every call; counts calls."""

    def __init__(self, response: ModelResponse) -> None:
        self._response = response
        self.calls = 0

    async def complete(self, spec, prompt, system_prompt, temperature, max_output_tokens) -> ModelResponse:
        self.calls += 1
        return self._response


class MappingClient(ModelClient):
    """Returns a response chosen by spec.model_name."""

    def __init__(self, by_model: dict[str, ModelResponse]) -> None:
        self._by_model = by_model

    async def complete(self, spec, prompt, system_prompt, temperature, max_output_tokens) -> ModelResponse:
        return self._by_model[spec.model_name]


class BlockingClient(ModelClient):
    """Blocks inside complete until released, tracking peak concurrency."""

    def __init__(self, release: asyncio.Event) -> None:
        self._release = release
        self.active = 0
        self.peak = 0

    async def complete(self, spec, prompt, system_prompt, temperature, max_output_tokens) -> ModelResponse:
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await self._release.wait()
        finally:
            self.active -= 1
        return ok_response()


class RecordingSleep:
    """Async sleep stand-in that records requested delays instead of waiting."""

    def __init__(self) -> None:
        self.delays: list[float] = []

    async def __call__(self, delay: float) -> None:
        self.delays.append(delay)
