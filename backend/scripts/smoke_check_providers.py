"""Manual smoke check: one real call to each compared model plus the judge.

Not a test — it reads real API keys from settings and hits the live
APIs, to prove the keys and model names work. Run manually:

    python -m scripts.smoke_check_providers

One call per model, no repeats, no retries, no loops beyond iterating
the four registered models.
"""

import asyncio
from decimal import Decimal

from app.config import settings
from evaluation.contracts import ModelResponse, ModelSpec
from evaluation.cost import compute_call_cost
from evaluation.providers.resolver import resolve_client
from evaluation.registry import get_compared_models, get_judge_model

_PROMPT = "What is the capital of France?"
_MAX_OUTPUT_TOKENS = 16
_TEMPERATURE = 0.0

# Reasoning tokens bill at the output rate and would dominate the cost of
# a call this small, so every call uses the lowest effort the OpenAI-
# compatible providers accept.
_LOWEST_REASONING_EFFORT = "low"

# Gemini's thinking tokens count against max_output_tokens, and the judge's
# per-model thinking level (registry: reasoning_level) is the lowest its model
# accepts. The judge still gets a larger budget than the compared models',
# since 16 tokens is too tight once the raw answer shares room with thinking.
_JUDGE_MAX_OUTPUT_TOKENS = 32

_ROW_FORMAT = (
    "{display_name:<28} {status:<7} {latency_ms:>7} "
    "in={input_tokens:<5} out={output_tokens:<5} cached={cached_tokens:<5} "
    "reasoning={reasoning_tokens:<5} estimated={tokens_estimated:<5} cost=${cost}"
)


async def _call_one(spec: ModelSpec) -> ModelResponse:
    is_judge = spec.provider == "google_ai_studio"

    client = resolve_client(
        spec,
        groq_api_key=settings.groq_api_key,
        nvidia_api_key=settings.nvidia_api_key,
        google_api_key=settings.google_api_key,
        reasoning_effort=_LOWEST_REASONING_EFFORT,
    )
    return await client.complete(
        spec,
        prompt=_PROMPT,
        system_prompt=None,
        temperature=_TEMPERATURE,
        max_output_tokens=_JUDGE_MAX_OUTPUT_TOKENS if is_judge else _MAX_OUTPUT_TOKENS,
    )


def _print_row(spec: ModelSpec, response: ModelResponse, cost: Decimal) -> None:
    print(
        _ROW_FORMAT.format(
            display_name=spec.display_name,
            status=response.status.value,
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
    specs = [*get_compared_models(), get_judge_model()]

    total_tokens = 0
    total_cost = Decimal("0")

    for spec in specs:
        try:
            response = await _call_one(spec)
        except Exception as error:  # belt-and-suspenders: adapters never raise, but don't let one bad model stop the run
            print(f"{spec.display_name:<28} crashed: {error}")
            continue

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
