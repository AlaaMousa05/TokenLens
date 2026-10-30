import asyncio
import hashlib
import random
from datetime import datetime, timezone
from decimal import Decimal

from evaluation.contracts import CallStatus, ModelClient, ModelResponse, ModelSpec, PriceSnapshot


class MockModelClient(ModelClient):
    """Fabricates responses without a network call, for building against the evaluation layer offline."""

    def __init__(
        self,
        min_latency_ms: int = 50,
        max_latency_ms: int = 50,
        failure_rate: float = 0.0,
        rate_limit_rate: float = 0.0,
        seed: int | None = None,
    ) -> None:
        if min_latency_ms < 0:
            raise ValueError("min_latency_ms must not be negative.")
        if max_latency_ms < min_latency_ms:
            raise ValueError("max_latency_ms must not be less than min_latency_ms.")
        if not 0.0 <= failure_rate <= 1.0:
            raise ValueError("failure_rate must be between 0 and 1.")
        if not 0.0 <= rate_limit_rate <= 1.0:
            raise ValueError("rate_limit_rate must be between 0 and 1.")
        if failure_rate + rate_limit_rate > 1.0:
            raise ValueError("failure_rate and rate_limit_rate must not sum above 1.")

        self._min_latency_ms = min_latency_ms
        self._max_latency_ms = max_latency_ms
        self._failure_rate = failure_rate
        self._rate_limit_rate = rate_limit_rate
        self._random = random.Random(seed)

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        latency_ms = self._random.randint(self._min_latency_ms, self._max_latency_ms)
        await asyncio.sleep(latency_ms / 1000)

        prices_snapshot = PriceSnapshot(
            input_price_per_mtok=spec.input_price_per_mtok,
            output_price_per_mtok=spec.output_price_per_mtok,
            cached_input_price_per_mtok=spec.cached_input_price_per_mtok,
            captured_at=datetime.now(timezone.utc),
        )

        roll = self._random.random()
        if roll < self._failure_rate:
            return self._failed_response(latency_ms, prices_snapshot, "Simulated provider error.")
        if roll < self._failure_rate + self._rate_limit_rate:
            return self._failed_response(latency_ms, prices_snapshot, "Simulated rate limit (429).")

        output_text = self._fabricate_output(spec, prompt, system_prompt, temperature)
        return ModelResponse(
            output_text=output_text,
            input_tokens=len(prompt.split()),
            output_tokens=len(output_text.split()),
            latency_ms=latency_ms,
            attempts=1,
            status=CallStatus.ok,
            tokens_estimated=True,
            prices_snapshot=prices_snapshot,
        )

    def _failed_response(self, latency_ms: int, prices_snapshot: PriceSnapshot, error_message: str) -> ModelResponse:
        return ModelResponse(
            output_text="",
            latency_ms=latency_ms,
            attempts=1,
            status=CallStatus.failed,
            error_message=error_message,
            tokens_estimated=True,
            prices_snapshot=prices_snapshot,
        )

    def _fabricate_output(self, spec: ModelSpec, prompt: str, system_prompt: str | None, temperature: float) -> str:
        hashed = f"{prompt}|{system_prompt}|{temperature}".encode()
        digest = hashlib.sha256(hashed).hexdigest()[:12]
        return f"[{spec.display_name}] mock-response-{digest} for prompt of {len(prompt.split())} word(s)."
