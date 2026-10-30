import httpx

from evaluation.contracts import CallStatus
from evaluation.providers._shared import DEFAULT_REQUEST_TIMEOUT_SECONDS
from evaluation.providers.openai_compatible import OpenAICompatibleClient
from tests.providers.conftest import make_spec


def _client(handler, api_key: str | None = "test-key") -> OpenAICompatibleClient:
    return OpenAICompatibleClient(
        base_url="https://example-provider.test/v1",
        api_key=api_key,
        transport=httpx.MockTransport(handler),
    )


async def test_reasoning_content_is_dropped_but_its_tokens_are_kept(groq_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "The final answer is 4.",
                            "reasoning_content": "Let me think step by step about 2+2...",
                        }
                    }
                ],
                "usage": {
                    "prompt_tokens": 12,
                    "completion_tokens": 6,
                    "completion_tokens_details": {"reasoning_tokens": 40},
                },
            },
        )

    response = await _client(handler).complete(groq_spec, "What is 2+2?", None, 0.0, 100)

    assert response.status == CallStatus.ok
    assert response.output_text == "The final answer is 4."
    assert "think" not in response.output_text
    assert response.reasoning_tokens == 40
    assert response.input_tokens == 12
    assert response.output_tokens == 6
    assert response.tokens_estimated is False


async def test_usage_mapping_includes_cached_tokens(nvidia_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "hello"}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 10,
                    "prompt_tokens_details": {"cached_tokens": 80},
                },
            },
        )

    response = await _client(handler).complete(nvidia_spec, "hi", "be nice", 0.5, 50)

    assert response.status == CallStatus.ok
    assert response.input_tokens == 100
    assert response.cached_tokens == 80
    assert response.output_tokens == 10
    assert response.reasoning_tokens == 0
    assert response.tokens_estimated is False


async def test_no_usage_object_falls_back_to_estimated_tokens(groq_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "a short reply"}}]})

    response = await _client(handler).complete(groq_spec, "a reasonably long prompt here", None, 0.0, 100)

    assert response.status == CallStatus.ok
    assert response.tokens_estimated is True
    assert response.input_tokens > 0
    assert response.output_tokens > 0


async def test_http_429_returns_failed_response_without_raising(groq_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": {"message": "rate limited"}})

    response = await _client(handler).complete(groq_spec, "hi", None, 0.0, 50)

    assert response.status == CallStatus.failed
    assert response.error_message is not None
    assert "429" in response.error_message
    assert response.attempts == 1


async def test_timeout_returns_failed_response_without_raising(groq_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out")

    response = await _client(handler).complete(groq_spec, "hi", None, 0.0, 50)

    assert response.status == CallStatus.failed
    assert "timed out" in response.error_message
    assert response.latency_ms >= 0


async def test_missing_api_key_fails_without_any_network_call(groq_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("no network call should happen without an API key")

    response = await _client(handler, api_key=None).complete(groq_spec, "hi", None, 0.0, 50)

    assert response.status == CallStatus.failed
    assert "groq" in response.error_message
    assert "key" in response.error_message.lower()


async def test_malformed_response_returns_failed_response(groq_spec) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    response = await _client(handler).complete(groq_spec, "hi", None, 0.0, 50)

    assert response.status == CallStatus.failed
    assert "Malformed response" in response.error_message


async def test_per_model_request_timeout_is_applied_to_the_http_client() -> None:
    spec = make_spec("groq", "openai/gpt-oss-120b", request_timeout_seconds=45.0)
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {}})

    await _client(handler).complete(spec, "hi", None, 0.0, 50)

    assert captured[0].extensions["timeout"]["read"] == 45.0


async def test_request_timeout_falls_back_when_spec_omits_it(groq_spec) -> None:
    assert groq_spec.request_timeout_seconds is None
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {}})

    await _client(handler).complete(groq_spec, "hi", None, 0.0, 50)

    assert captured[0].extensions["timeout"]["read"] == DEFAULT_REQUEST_TIMEOUT_SECONDS
