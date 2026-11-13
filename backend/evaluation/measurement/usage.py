"""Tallies tokens and cost across every call, so a run's totals cover candidate and judge calls alike.

A measurement observer, not judging or provider logic: it forwards to the wrapped
client and records what came back.
"""

from decimal import Decimal

from evaluation.contracts import ModelClient, ModelResponse, ModelSpec
from evaluation.cost import compute_call_cost


class UsageRecorder(ModelClient):
    """Forwards to an inner client and accumulates tokens and cost from each response."""

    def __init__(self, inner: ModelClient) -> None:
        self._inner = inner
        self.calls = 0
        self.total_tokens = 0
        self.total_cost = Decimal("0")

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        response = await self._inner.complete(spec, prompt, system_prompt, temperature, max_output_tokens)
        self.calls += 1
        self.total_tokens += (
            response.input_tokens + response.output_tokens + response.cached_tokens + response.reasoning_tokens
        )
        self.total_cost += compute_call_cost(response).total_cost
        return response
