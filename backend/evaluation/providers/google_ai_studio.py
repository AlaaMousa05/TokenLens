

import time
from typing import Any

import httpx

from evaluation.contracts import CallStatus, ModelClient, ModelResponse, ModelSpec, PriceSnapshot
from evaluation.providers._shared import (
    build_price_snapshot,
    elapsed_ms,
    estimate_tokens,
    failed_response,
    resolve_timeout_seconds,
)

_API_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"


_FALLBACK_THINKING_LEVEL = "low"


class GoogleAIStudioClient(ModelClient):
  
    def __init__(
        self,
        api_key: str | None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_key = api_key
        self._transport = transport

    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:
        prices_snapshot = build_price_snapshot(spec)

        if not self._api_key:
            return failed_response(0, prices_snapshot, f"No API key configured for provider '{spec.provider}'.")

        payload: dict[str, Any] = {
            "model": spec.model_name,
            "input": prompt,
            "generation_config": {
                "max_output_tokens": max_output_tokens,
                "thinking_level": spec.reasoning_level or _FALLBACK_THINKING_LEVEL,
            },
        }
        if system_prompt:
            payload["system_instruction"] = system_prompt

        headers = {"x-goog-api-key": self._api_key}
        timeout_seconds = resolve_timeout_seconds(spec)

        started_at = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, transport=self._transport) as client:
                response = await client.post(_API_URL, json=payload, headers=headers)
            latency_ms = elapsed_ms(started_at)
            response.raise_for_status()
            data = response.json()
        except httpx.TimeoutException:
            return failed_response(
                elapsed_ms(started_at),
                prices_snapshot,
                f"Request to {spec.provider} timed out after {timeout_seconds}s.",
            )
        except httpx.HTTPStatusError as error:
            return failed_response(elapsed_ms(started_at), prices_snapshot, _status_error_message(spec, error))
        except httpx.HTTPError as error:
            return failed_response(elapsed_ms(started_at), prices_snapshot, f"Request to {spec.provider} failed: {error}.")

        try:
            return _parse_success(data, prompt, system_prompt, latency_ms, prices_snapshot)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            return failed_response(latency_ms, prices_snapshot, f"Malformed response from {spec.provider}: {error}.")


def _status_error_message(spec: ModelSpec, error: httpx.HTTPStatusError) -> str:
    status_code = error.response.status_code
    if status_code == 429:
        return f"{spec.provider} rate limit (429) hit for {spec.model_name}."
    return f"{spec.provider} returned HTTP {status_code} for {spec.model_name}: {error.response.text[:200]}"


def _parse_success(
    data: dict[str, Any],  
    prompt: str,
    system_prompt: str | None,
    latency_ms: int,
    prices_snapshot: PriceSnapshot,
) -> ModelResponse:
    output_text = "".join(
        content_item.get("text", "")
        for step in data["steps"]
        if step.get("type") == "model_output"
        for content_item in step.get("content", [])
        if content_item.get("type") == "text"
    )

    usage = data.get("usage")
    if usage is None:
        input_tokens = estimate_tokens(f"{system_prompt or ''} {prompt}")
        output_tokens = estimate_tokens(output_text)
        cached_tokens = 0
        reasoning_tokens = 0
        tokens_estimated = True
    else:
        input_tokens = usage.get("total_input_tokens", 0)
        output_tokens = usage.get("total_output_tokens", 0)
        cached_tokens = usage.get("total_cached_tokens", 0)
        reasoning_tokens = usage.get("total_thought_tokens", 0)
        tokens_estimated = False

    return ModelResponse(
        output_text=output_text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        reasoning_tokens=reasoning_tokens,
        latency_ms=latency_ms,
        attempts=1,
        status=CallStatus.ok,
        tokens_estimated=tokens_estimated,
        prices_snapshot=prices_snapshot,
    )
