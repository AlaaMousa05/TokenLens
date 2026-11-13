"""Cache savings from the caching layer's own counters plus the responses it served on hits."""

from dataclasses import dataclass
from decimal import Decimal

from evaluation.contracts import ModelResponse
from evaluation.cost import compute_call_cost
from evaluation.execution.caching_client import CacheStats


@dataclass(frozen=True)
class CacheSavings:
    """What caching avoided over a run."""

    hits: int
    misses: int
    hit_rate: Decimal
    tokens_saved: int
    cost_avoided: Decimal


def cache_savings(stats: CacheStats, served_on_hits: list[ModelResponse]) -> CacheSavings:
    """Tokens and cost avoided are those of the responses served from cache instead of re-called."""
    tokens_saved = sum(
        response.input_tokens + response.output_tokens + response.cached_tokens + response.reasoning_tokens
        for response in served_on_hits
    )
    cost_avoided = sum((compute_call_cost(response).total_cost for response in served_on_hits), Decimal("0"))
    return CacheSavings(
        hits=stats.hits,
        misses=stats.misses,
        hit_rate=Decimal(str(stats.hit_rate)).quantize(Decimal("0.001")),
        tokens_saved=tokens_saved,
        cost_avoided=cost_avoided,
    )
