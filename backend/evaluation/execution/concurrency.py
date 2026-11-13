"""Caps in-flight calls per provider, since rate limits are per provider, not per model."""

import asyncio

from evaluation.contracts import ModelClient, ModelResponse, ModelSpec

DEFAULT_PROVIDER_CONCURRENCY = 4


class ProviderConcurrency:
    """One semaphore per provider, shared by every model on that provider."""

    def __init__(self, limits: dict[str, int] | None = None, default: int = DEFAULT_PROVIDER_CONCURRENCY) -> None:
        self._limits = dict(limits or {})
        self._default = default
        self._semaphores: dict[str, asyncio.Semaphore] = {}

    def slot(self, provider: str) -> asyncio.Semaphore:
        if provider not in self._semaphores:
            self._semaphores[provider] = asyncio.Semaphore(self._limits.get(provider, self._default))
        return self._semaphores[provider]


class ConcurrencyLimitedClient(ModelClient):
    """Holds the provider's slot for the duration of the wrapped call."""

    def __init__(self, inner: ModelClient, concurrency: ProviderConcurrency) -> None:
        self._inner = inner
        self._concurrency = concurrency

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        async with self._concurrency.slot(spec.provider):
            return await self._inner.complete(spec, prompt, system_prompt, temperature, max_output_tokens)
