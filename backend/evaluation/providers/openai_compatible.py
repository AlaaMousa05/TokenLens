

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

DEFAULT_REASONING_EFFORT = "medium"


class OpenAICompatibleClient(ModelClient):
    

    def __init__(
        self,
        base_url: str,
        api_key: str | None,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._reasoning_effort = reasoning_effort
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

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": spec.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "reasoning_effort": self._reasoning_effort,
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        timeout_seconds = resolve_timeout_seconds(spec)

        started_at = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=timeout_seconds, transport=self._transport) as client:
                response = await client.post(f"{self._base_url}/chat/completions", json=payload, headers=headers)
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
            return _parse_success(spec, data, prompt, system_prompt, latency_ms, prices_snapshot)
        except (KeyError, IndexError, TypeError, ValueError) as error:
            return failed_response(latency_ms, prices_snapshot, f"Malformed response from {spec.provider}: {error}.")


def _status_error_message(spec: ModelSpec, error: httpx.HTTPStatusError) -> str:
    status_code = error.response.status_code
    if status_code == 429:
        return f"{spec.provider} rate limit (429) hit for {spec.model_name}."
    return f"{spec.provider} returned HTTP {status_code} for {spec.model_name}: {error.response.text[:200]}"


def _parse_success(
    spec: ModelSpec,
    data: dict[str, Any],  
    prompt: str,
    system_prompt: str | None,
    latency_ms: int,
    prices_snapshot: PriceSnapshot,
) -> ModelResponse:
    message = data["choices"][0]["message"]
    output_text = message.get("content") or ""
    reasoning_text = message.get("reasoning_content") or message.get("reasoning") or ""

    usage = data.get("usage")
    if usage is None:
        input_tokens = estimate_tokens(f"{system_prompt or ''} {prompt}")
        output_tokens = estimate_tokens(output_text)
        reasoning_tokens = estimate_tokens(reasoning_text)
        cached_tokens = 0
        tokens_estimated = True
    else:
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cached_tokens = (usage.get("prompt_tokens_details") or {}).get("cached_tokens", 0)
        reasoning_tokens = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens", 0)
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
