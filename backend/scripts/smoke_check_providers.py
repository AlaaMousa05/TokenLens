"""Manual smoke check: one call to each compared model and each judge.

Not a test — it reads real API keys from settings and hits the live APIs,
to prove the keys and model names work. Calls go through the execution
layer with retries on and caching off, so the attempts column shows how
much retrying recovers. Run manually:

    python -m scripts.smoke_check_providers
"""

import asyncio
from decimal import Decimal

from app.config import settings
from evaluation.contracts import ModelClient, ModelResponse, ModelSpec
from evaluation.cost import compute_call_cost
from evaluation.execution import InMemoryCache, ProviderConcurrency, RetryPolicy, build_execution_client
from evaluation.execution.caching_client import CacheStats
from evaluation.providers.resolver import resolve_client
from evaluation.registry import get_compared_models, list_judge_models

_PROMPT = "What is the capital of France?"
_MAX_OUTPUT_TOKENS = 16
_TEMPERATURE = 0.0

# Reasoning and thinking tokens count against the output budget, so judges get a
# larger one — 16 tokens is too tight once a reasoning model shares the budget
# between its thinking and the raw answer.
_JUDGE_MAX_OUTPUT_TOKENS = 256

_ROW_FORMAT = (
    "{display_name:<28} {status:<7} {outcome:<10} att={attempts:<2} {latency_ms:>8} "
    "in={input_tokens:<5} out={output_tokens:<5} cached={cached_tokens:<5} "
    "reasoning={reasoning_tokens:<5} estimated={tokens_estimated:<5} cost=${cost}"
)


def _build_client() -> ModelClient:
    execution = build_execution_client(
        resolve=lambda spec: resolve_client(
            spec,
            google_api_key=settings.google_api_key,
            azure_api_key=settings.azure_api_key,
        ),
        concurrency=ProviderConcurrency(),
        cache_backend=InMemoryCache(),
        cache_stats=CacheStats(),
        retry_policy=RetryPolicy(),
    )
    return execution.select(use_cache=False)


async def _call_one(client: ModelClient, spec: ModelSpec) -> ModelResponse:
    max_output_tokens = _JUDGE_MAX_OUTPUT_TOKENS if spec.is_judge_eligible else _MAX_OUTPUT_TOKENS
    return await client.complete(spec, _PROMPT, None, _TEMPERATURE, max_output_tokens)


def _print_row(spec: ModelSpec, response: ModelResponse, cost: Decimal) -> None:
    outcome = response.completion_outcome.value if response.completion_outcome is not None else "-"
    print(
        _ROW_FORMAT.format(
            display_name=spec.display_name,
            status=response.status.value,
            outcome=outcome,
            attempts=response.attempts,
            latency_ms=f"{response.latency_ms}ms",
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cached_tokens=response.cached_tokens,
            reasoning_tokens=response.reasoning_tokens,
            tokens_estimated=str(response.tokens_estimated),
            cost=cost,
        )
    )
    if response.error_message is not None:
        print(f"  error: {response.error_message}")


async def main() -> None:
    client = _build_client()
    specs = [*get_compared_models(), *list_judge_models()]

    total_tokens = 0
    total_cost = Decimal("0")

    for spec in specs:
        response = await _call_one(client, spec)
        breakdown = compute_call_cost(response)
        total_tokens += (
            response.input_tokens + response.output_tokens + response.cached_tokens + response.reasoning_tokens
        )
        total_cost += breakdown.total_cost
        _print_row(spec, response, breakdown.total_cost)

    print()
    print(f"total tokens: {total_tokens}")
    print(f"total cost:   ${total_cost}")


if __name__ == "__main__":
    asyncio.run(main())
