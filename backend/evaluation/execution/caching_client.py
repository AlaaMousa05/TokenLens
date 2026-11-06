"""Serves cached successful responses and records hit/miss counts.

Only a normal, successful completion is cached — never a failure and never a
non-normal outcome, which must be re-measured rather than frozen.
"""

import hashlib
import json
from dataclasses import dataclass

from evaluation.contracts import CallStatus, CompletionOutcome, ModelClient, ModelResponse, ModelSpec
from evaluation.execution.cache import CacheBackend


@dataclass
class CacheStats:
    """Running hit/miss tally for a run, for reporting token savings."""

    hits: int = 0
    misses: int = 0

    @property
    def lookups(self) -> int:
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        return self.hits / self.lookups if self.lookups else 0.0


def cache_key(
    spec: ModelSpec,
    prompt: str,
    system_prompt: str | None,
    temperature: float,
    max_output_tokens: int,
) -> str:
    """Hash of everything that can change the output, so a changed input misses the cache."""
    payload = json.dumps(
        {
            "model_name": spec.model_name,
            "system_prompt": system_prompt,
            "prompt": prompt,
            "temperature": temperature,
            "max_output_tokens": max_output_tokens,
            "reasoning_level": spec.reasoning_level,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode()).hexdigest()


class CachingClient(ModelClient):
    """Returns a cached normal response on a hit; otherwise calls through and caches a normal success."""

    def __init__(self, inner: ModelClient, backend: CacheBackend, stats: CacheStats) -> None:
        self._inner = inner
        self._backend = backend
        self._stats = stats

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        key = cache_key(spec, prompt, system_prompt, temperature, max_output_tokens)
        cached = await self._backend.get(key)
        if cached is not None:
            self._stats.hits += 1
            return cached
        self._stats.misses += 1
        response = await self._inner.complete(spec, prompt, system_prompt, temperature, max_output_tokens)
        if response.status is CallStatus.ok and response.completion_outcome is CompletionOutcome.normal:
            await self._backend.set(key, response)
        return response
