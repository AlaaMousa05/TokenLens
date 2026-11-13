"""Measure cache savings on a realistic re-run: populate the cache, then re-run and reuse it.

Reports hit rate, tokens saved and cost avoided from the caching layer's counters.

    python -m scripts.cache_savings
"""

import asyncio

from evaluation.measurement.cache_savings import cache_savings
from evaluation.registry import get_compared_models
from scripts._harness import load_policy, load_rows, new_execution

_CANDIDATE_MAX_TOKENS = 512


async def main() -> None:
    models = get_compared_models()
    policy, rows = load_policy(), load_rows()
    execution, stats = new_execution(use_cache=True)
    client = execution.select(use_cache=True)

    for model in models:
        for row in rows:
            await client.complete(model, row.question, policy, 0.0, _CANDIDATE_MAX_TOKENS)

    served_on_hits = []
    for model in models:
        for row in rows:
            served_on_hits.append(await client.complete(model, row.question, policy, 0.0, _CANDIDATE_MAX_TOKENS))

    savings = cache_savings(stats, served_on_hits)
    print("=== Cache savings (populate, then re-run) ===")
    print(f"  hits={savings.hits}  misses={savings.misses}  hit_rate={savings.hit_rate}")
    print(f"  tokens_saved={savings.tokens_saved}  cost_avoided=${savings.cost_avoided}")


if __name__ == "__main__":
    asyncio.run(main())
