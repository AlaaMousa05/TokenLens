

import time
from datetime import datetime, timezone

from evaluation.contracts import CallStatus, ModelResponse, ModelSpec, PriceSnapshot

_ESTIMATED_TOKENS_PER_WORD = 1.3


DEFAULT_REQUEST_TIMEOUT_SECONDS = 30.0


def resolve_timeout_seconds(spec: ModelSpec) -> float:
    """Per-model request deadline, falling back to the shared default when the spec omits one."""
    return spec.request_timeout_seconds or DEFAULT_REQUEST_TIMEOUT_SECONDS


def build_price_snapshot(spec: ModelSpec) -> PriceSnapshot:
    """Freeze spec's current prices at call time."""
    return PriceSnapshot(
        input_price_per_mtok=spec.input_price_per_mtok,
        output_price_per_mtok=spec.output_price_per_mtok,
        cached_input_price_per_mtok=spec.cached_input_price_per_mtok,
        captured_at=datetime.now(timezone.utc),
    )


def estimate_tokens(text: str) -> int:
    """Rough word-count-based token estimate for providers that report no usage at all."""
    if not text:
        return 0
    word_count = len(text.split())
    return max(1, round(word_count * _ESTIMATED_TOKENS_PER_WORD))


def elapsed_ms(started_at: float) -> int:
    """Milliseconds since started_at, a time.monotonic() reading taken before the request."""
    return round((time.monotonic() - started_at) * 1000)


def failed_response(latency_ms: int, prices_snapshot: PriceSnapshot, error_message: str) -> ModelResponse:
    """The shape every adapter returns on a provider error, timeout, or malformed response."""
    return ModelResponse(
        output_text="",
        latency_ms=latency_ms,
        attempts=1,
        status=CallStatus.failed,
        error_message=error_message,
        tokens_estimated=False,
        prices_snapshot=prices_snapshot,
    )
