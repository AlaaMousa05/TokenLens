import pytest

from evaluation.providers.google_ai_studio import GoogleAIStudioClient
from evaluation.providers.openai_compatible import OpenAICompatibleClient
from evaluation.providers.resolver import resolve_client
from tests.providers.conftest import make_spec


def test_resolves_groq_spec_to_openai_compatible_client() -> None:
    client = resolve_client(
        make_spec("groq", "openai/gpt-oss-120b"),
        groq_api_key="groq-key",
        nvidia_api_key=None,
        google_api_key=None,
    )

    assert isinstance(client, OpenAICompatibleClient)


def test_resolves_nvidia_nim_spec_to_openai_compatible_client() -> None:
    client = resolve_client(
        make_spec("nvidia_nim", "openai/gpt-oss-20b"),
        groq_api_key=None,
        nvidia_api_key="nvidia-key",
        google_api_key=None,
    )

    assert isinstance(client, OpenAICompatibleClient)


def test_resolves_google_ai_studio_spec_to_its_own_client() -> None:
    client = resolve_client(
        make_spec("google_ai_studio", "gemini-3.8-flash"),
        groq_api_key=None,
        nvidia_api_key=None,
        google_api_key="google-key",
    )

    assert isinstance(client, GoogleAIStudioClient)


def test_unknown_provider_fails_loudly_naming_it_and_the_supported_ones() -> None:
    with pytest.raises(ValueError) as excinfo:
        resolve_client(
            make_spec("mystery_provider", "some-model"),
            groq_api_key=None,
            nvidia_api_key=None,
            google_api_key=None,
        )

    message = str(excinfo.value)
    assert "mystery_provider" in message
    assert "groq" in message
    assert "nvidia_nim" in message
    assert "google_ai_studio" in message
