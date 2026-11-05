"""Offline demo of the execution layer: one prompt, three compared models, 3 repeats.

Uses MockModelClient — no network, no keys. Shows a per-model latency
distribution from a fresh (cache-off) variance run, then a cache-on pass to
report hit rate and the tokens caching saved. Run manually:

    python -m scripts.demo_execution
"""

import asyncio
import statistics
from decimal import Decimal

from evaluation.contracts import ModelResponse
from evaluation.cost import compute_call_cost
from evaluation.execution import (
    InMemoryCache,
    ProviderConcurrency,
    RetryPolicy,
    build_execution_client,
    fan_out,
)
from evaluation.execution.caching_client import CacheStats
from evaluation.mock_client import MockModelClient
from evaluation.registry import get_compared_models

_PROMPT = "Name one city."
_MAX_OUTPUT_TOKENS = 64
_REPEATS = 3

_ROW_FORMAT = "{display_name:<28} {outcome:<8} att={attempts:<2} mean={mean_ms:>7.1f}ms stdev={stdev_ms:>6.1f}ms cost=${cost}"


def _billable_tokens(response: ModelResponse) -> int:
    return response.input_tokens + response.output_tokens + response.cached_tokens + response.reasoning_tokens


def _build_execution(stats: CacheStats):
    mock = MockModelClient(min_latency_ms=50, max_latency_ms=250, seed=7)
    return build_execution_client(
        resolve=lambda spec: mock,
        concurrency=ProviderConcurrency(),
        cache_backend=InMemoryCache(),
        cache_stats=stats,
        retry_policy=RetryPolicy(),
    )


async def _variance_run(execution, specs) -> Decimal:
    results = await fan_out(
        execution.select(use_cache=False), specs, _PROMPT, max_output_tokens=_MAX_OUTPUT_TOKENS, repeats=_REPEATS
    )
    total_cost = Decimal("0")
    print(f"Variance run (caching off, {_REPEATS} repeats):")
    for result in results:
        latencies = [r.latency_ms for r in result.responses]
        model_cost = sum((compute_call_cost(r).total_cost for r in result.responses), Decimal("0"))
        total_cost += model_cost
        print(
            _ROW_FORMAT.format(
                display_name=result.spec.display_name,
                outcome=result.responses[0].completion_outcome.value,
                attempts=max(r.attempts for r in result.responses),
                mean_ms=statistics.mean(latencies),
                stdev_ms=statistics.stdev(latencies),
                cost=model_cost,
            )
        )
    return total_cost


async def _cache_run(execution, specs, stats: CacheStats) -> None:
    await fan_out(execution.select(use_cache=True), specs, _PROMPT, max_output_tokens=_MAX_OUTPUT_TOKENS)
    served = await fan_out(execution.select(use_cache=True), specs, _PROMPT, max_output_tokens=_MAX_OUTPUT_TOKENS)

    tokens_saved = sum(_billable_tokens(result.responses[0]) for result in served)
    cost_avoided = sum((compute_call_cost(result.responses[0]).total_cost for result in served), Decimal("0"))
    print("\nCache run (caching on, warm then reuse):")
    print(f"  hit rate:     {stats.hit_rate:.0%} ({stats.hits} hits / {stats.lookups} lookups)")
    print(f"  tokens saved: {tokens_saved}")
    print(f"  cost avoided: ${cost_avoided}")


async def main() -> None:
    specs = get_compared_models()
    stats = CacheStats()
    execution = _build_execution(stats)

    total_cost = await _variance_run(execution, specs)
    print(f"\ntotal cost (variance run): ${total_cost}")
    await _cache_run(execution, specs, stats)


if __name__ == "__main__":
    asyncio.run(main())
