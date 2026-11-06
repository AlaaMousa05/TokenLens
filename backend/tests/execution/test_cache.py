from evaluation.contracts import CompletionOutcome
from evaluation.execution.cache import FileCache, InMemoryCache
from evaluation.execution.caching_client import CacheStats, CachingClient
from evaluation.execution.composition import build_execution_client
from evaluation.execution.concurrency import ProviderConcurrency
from evaluation.execution.retry import RetryPolicy
from tests.execution.conftest import (
    CountingClient,
    failed_response,
    make_spec,
    non_normal_response,
    ok_response,
)

_SPEC = make_spec("azure_ai_foundry")


async def _call(client):
    return await client.complete(_SPEC, "p", None, 0.0, 16)


async def test_hit_avoids_a_second_call() -> None:
    inner = CountingClient(ok_response())
    stats = CacheStats()
    client = CachingClient(inner, InMemoryCache(), stats)

    first = await _call(client)
    second = await _call(client)

    assert inner.calls == 1
    assert stats.hits == 1 and stats.misses == 1
    assert second.output_text == first.output_text


async def test_failed_call_is_not_cached() -> None:
    inner = CountingClient(failed_response("azure rate limit (429) hit for m."))
    stats = CacheStats()
    client = CachingClient(inner, InMemoryCache(), stats)

    await _call(client)
    await _call(client)

    assert inner.calls == 2
    assert stats.hits == 0


async def test_non_normal_completion_is_not_cached() -> None:
    inner = CountingClient(non_normal_response(CompletionOutcome.truncated))
    stats = CacheStats()
    client = CachingClient(inner, InMemoryCache(), stats)

    await _call(client)
    await _call(client)

    assert inner.calls == 2
    assert stats.hits == 0


async def test_caching_disabled_produces_fresh_calls() -> None:
    inner = CountingClient(ok_response())
    stats = CacheStats()
    execution = build_execution_client(
        resolve=lambda spec: inner,
        concurrency=ProviderConcurrency(),
        cache_backend=InMemoryCache(),
        cache_stats=stats,
        retry_policy=RetryPolicy(),
    )

    await execution.select(use_cache=False).complete(_SPEC, "p", None, 0.0, 16)
    await execution.select(use_cache=False).complete(_SPEC, "p", None, 0.0, 16)

    assert inner.calls == 2
    assert stats.lookups == 0


async def test_file_cache_round_trips_a_response(tmp_path) -> None:
    backend = FileCache(tmp_path)
    response = ok_response(input_tokens=42, output_tokens=7)

    await backend.set("key", response)
    restored = await backend.get("key")

    assert restored is not None
    assert restored.model_dump() == response.model_dump()
