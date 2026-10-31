import json

import httpx

from evaluation.contracts import CallStatus
from evaluation.providers._shared import DEFAULT_REQUEST_TIMEOUT_SECONDS
from evaluation.providers.google_ai_studio import _FALLBACK_THINKING_LEVEL, GoogleAIStudioClient
from tests.providers.conftest import make_spec


def _client(handler, api_key: str | None = "test-key") -> GoogleAIStudioClient:
    return GoogleAIStudioClient(api_key=api_key, transport=httpx.MockTransport(handler))


def _ok_handler(captured: list[httpx.Request]):
    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200,
            json={
                "id": "v1_test",
                "model": "gemini-3.8-flash",
                "object": "interaction",
                "status": "completed",
                "steps": [{"type": "model_output", "content": [{"type": "text", "text": "ok"}]}],
            },
        )

    return handler


async def test_usage_maps_cached_and_thinking_tokens(gemini_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "v1_test",
                "model": "gemini-3.8-flash",
                "object": "interaction",
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "The verdict is model A."}],
                    }
                ],
                "usage": {
                    "input_tokens_by_modality": [{"modality": "text", "tokens": 500}],
                    "total_cached_tokens": 300,
                    "total_input_tokens": 500,
                    "total_output_tokens": 20,
                    "total_thought_tokens": 150,
                    "total_tokens": 970,
                    "total_tool_use_tokens": 0,
                },
            },
        )

    response = await _client(handler).complete(gemini_spec, "grade this", "be fair", 0.0, 200)

    assert response.status == CallStatus.ok
    assert response.output_text == "The verdict is model A."
    assert response.input_tokens == 500
    assert response.output_tokens == 20
    assert response.cached_tokens == 300
    assert response.reasoning_tokens == 150
    assert response.tokens_estimated is False


async def test_no_usage_falls_back_to_estimated_tokens(gemini_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": "v1_test",
                "model": "gemini-3.8-flash",
                "object": "interaction",
                "status": "completed",
                "steps": [
                    {
                        "type": "model_output",
                        "content": [{"type": "text", "text": "a short verdict"}],
                    }
                ],
            },
        )

    response = await _client(handler).complete(gemini_spec, "a reasonably long prompt here", None, 0.0, 200)

    assert response.status == CallStatus.ok
    assert response.tokens_estimated is True
    assert response.input_tokens > 0
    assert response.output_tokens > 0


async def test_http_429_returns_failed_response_without_raising(gemini_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "rate limited"}})

    response = await _client(handler).complete(gemini_spec, "grade this", None, 0.0, 200)

    assert response.status == CallStatus.failed
    assert "429" in response.error_message
    assert response.attempts == 1


async def test_timeout_returns_failed_response_without_raising(gemini_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    response = await _client(handler).complete(gemini_spec, "grade this", None, 0.0, 200)

    assert response.status == CallStatus.failed
    assert "timed out" in response.error_message


async def test_missing_api_key_fails_without_any_network_call(gemini_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no network call should happen without an API key")

    response = await _client(handler, api_key=None).complete(gemini_spec, "grade this", None, 0.0, 200)

    assert response.status == CallStatus.failed
    assert "google_ai_studio" in response.error_message


async def test_api_key_sent_as_header_not_query_param(gemini_spec) -> None:
    captured: list[httpx.Request] = []

    await _client(_ok_handler(captured), api_key="secret-key").complete(gemini_spec, "grade this", None, 0.0, 200)

    assert len(captured) == 1
    request = captured[0]
    assert request.headers["x-goog-api-key"] == "secret-key"
    assert "key" not in request.url.params


async def test_per_model_reasoning_level_is_sent_as_thinking_level(gemini_spec) -> None:
    captured: list[httpx.Request] = []

    await _client(_ok_handler(captured)).complete(gemini_spec, "grade this", None, 0.0, 200)

    body = json.loads(captured[0].content)
    assert body["generation_config"]["thinking_level"] == gemini_spec.reasoning_level == "low"


async def test_thinking_level_falls_back_when_spec_omits_reasoning_level() -> None:
    spec_without_level = make_spec("google_ai_studio", "gemini-3.8-flash")
    assert spec_without_level.reasoning_level is None
    captured: list[httpx.Request] = []

    await _client(_ok_handler(captured)).complete(spec_without_level, "grade this", None, 0.0, 200)

    body = json.loads(captured[0].content)
    assert body["generation_config"]["thinking_level"] == _FALLBACK_THINKING_LEVEL


async def test_per_model_request_timeout_is_applied_to_the_http_client() -> None:
    spec = make_spec("google_ai_studio", "gemini-3.8-flash", request_timeout_seconds=120.0)
    captured: list[httpx.Request] = []

    await _client(_ok_handler(captured)).complete(spec, "grade this", None, 0.0, 200)

    assert captured[0].extensions["timeout"]["read"] == 120.0


async def test_request_timeout_falls_back_when_spec_omits_it() -> None:
    spec_without_timeout = make_spec("google_ai_studio", "gemini-3.8-flash")
    assert spec_without_timeout.request_timeout_seconds is None
    captured: list[httpx.Request] = []

    await _client(_ok_handler(captured)).complete(spec_without_timeout, "grade this", None, 0.0, 200)

    assert captured[0].extensions["timeout"]["read"] == DEFAULT_REQUEST_TIMEOUT_SECONDS


async def test_malformed_response_returns_failed_response(gemini_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    response = await _client(handler).complete(gemini_spec, "grade this", None, 0.0, 200)

    assert response.status == CallStatus.failed
    assert "Malformed response" in response.error_message
