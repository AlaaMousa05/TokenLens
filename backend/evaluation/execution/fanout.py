"""Runs one prompt across several models (and repeats) concurrently.

One model failing, timing out, or exhausting its retries never cancels or
delays the others; results come back in input order.
"""

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass

from evaluation.contracts import ModelClient, ModelResponse, ModelSpec


@dataclass(frozen=True)
class FanOutResult:
    """Every response for one model, one per repeat, in repeat order."""

    spec: ModelSpec
    responses: list[ModelResponse]


async def fan_out(
    client: ModelClient,
    specs: Sequence[ModelSpec],
    prompt: str,
    *,
    system_prompt: str | None = None,
    temperature: float = 0.0,
    max_output_tokens: int,
    repeats: int = 1,
) -> list[FanOutResult]:
    """Call every spec `repeats` times concurrently; isolation and ordering come from the frozen never-raise contract."""

    async def run_spec(spec: ModelSpec) -> FanOutResult:
        calls = [
            client.complete(spec, prompt, system_prompt, temperature, max_output_tokens) for _ in range(repeats)
        ]
        return FanOutResult(spec=spec, responses=list(await asyncio.gather(*calls)))

    return list(await asyncio.gather(*(run_spec(spec) for spec in specs)))
