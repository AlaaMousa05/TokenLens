"""The one place the execution layers are assembled, in the fixed order
cache -> concurrency -> retry -> adapter.

Callers never wire the decorators themselves, so the order cannot be got wrong.
"""

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from evaluation.contracts import ModelClient, ModelResponse, ModelSpec
from evaluation.execution.cache import CacheBackend
from evaluation.execution.caching_client import CacheStats, CachingClient
from evaluation.execution.concurrency import ConcurrencyLimitedClient, ProviderConcurrency
from evaluation.execution.retry import RetryingClient, RetryPolicy


class _ResolvingClient(ModelClient):
    """Innermost layer: picks the provider adapter for each spec at call time."""

    def __init__(self, resolve: Callable[[ModelSpec], ModelClient]) -> None:
        self._resolve = resolve

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        return await self._resolve(spec).complete(spec, prompt, system_prompt, temperature, max_output_tokens)


@dataclass(frozen=True)
class ExecutionClient:
    """A composed client with and without caching; `select` picks per call."""

    cached: ModelClient
    direct: ModelClient

    def select(self, use_cache: bool) -> ModelClient:
        return self.cached if use_cache else self.direct


def build_execution_client(
    *,
    resolve: Callable[[ModelSpec], ModelClient],
    concurrency: ProviderConcurrency,
    cache_backend: CacheBackend,
    cache_stats: CacheStats,
    retry_policy: RetryPolicy,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    rng: random.Random | None = None,
) -> ExecutionClient:
    """Stack the layers once. `direct` skips only the cache; concurrency and retry always apply."""
    adapter = _ResolvingClient(resolve)
    retrying = RetryingClient(adapter, retry_policy, sleep=sleep, rng=rng)
    limited = ConcurrencyLimitedClient(retrying, concurrency)
    caching = CachingClient(limited, cache_backend, cache_stats)
    return ExecutionClient(cached=caching, direct=limited)
