"""Retries a wrapped ModelClient on transient failures with jittered backoff.

Transience is read from the ModelResponse the frozen adapters already return
(status plus error_message); the adapters themselves stay single-attempt.
"""

import asyncio
import random
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from evaluation.contracts import CallStatus, ModelClient, ModelResponse, ModelSpec

_HTTP_STATUS = re.compile(r"HTTP (\d{3})")


@dataclass(frozen=True)
class RetryPolicy:
    """Bounds on retrying one call: how many tries, how long to back off, and a total-time ceiling."""

    max_attempts: int = 3
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 8.0
    max_elapsed_seconds: float = 30.0


def is_retryable(response: ModelResponse) -> bool:
    """Whether a failed response is worth retrying: a timeout, 429, 5xx, or transport error, never a 4xx."""
    if response.status is not CallStatus.failed:
        return False
    message = response.error_message or ""
    if "timed out" in message or "(429)" in message:
        return True
    status_match = _HTTP_STATUS.search(message)
    if status_match:
        return 500 <= int(status_match.group(1)) <= 599
    return "failed:" in message


class RetryingClient(ModelClient):
    """Wraps a ModelClient so a transient failure is retried; records the real attempt count and never raises."""

    def __init__(
        self,
        inner: ModelClient,
        policy: RetryPolicy,
        *,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        rng: random.Random | None = None,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self._inner = inner
        self._policy = policy
        self._sleep = sleep
        self._rng = rng or random.Random()
        self._monotonic = monotonic

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        started_at = self._monotonic()
        attempt = 0
        while True:
            attempt += 1
            response = (await self._inner.complete(spec, prompt, system_prompt, temperature, max_output_tokens)).model_copy(
                update={"attempts": attempt}
            )
            if response.status is CallStatus.ok or not is_retryable(response) or attempt >= self._policy.max_attempts:
                return response
            delay = self._next_delay(response, attempt)
            if self._monotonic() - started_at + delay > self._policy.max_elapsed_seconds:
                return response
            await self._sleep(delay)

    def _next_delay(self, response: ModelResponse, attempt: int) -> float:
        if response.retry_after_seconds is not None:
            return response.retry_after_seconds
        capped = min(self._policy.max_delay_seconds, self._policy.base_delay_seconds * (2 ** (attempt - 1)))
        return self._rng.uniform(0, capped)
