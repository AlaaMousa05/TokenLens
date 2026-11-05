import pytest

from evaluation.providers.google_ai_studio import GoogleAIStudioClient
from evaluation.providers.openai_compatible import OpenAICompatibleClient
from evaluation.providers.resolver import resolve_client
from tests.providers.conftest import make_spec

_NO_KEYS = {"google_api_key": None, "azure_api_key": None}


def test_resolves_azure_spec_to_openai_compatible_client() -> None:
    client = resolve_client(make_spec("azure_ai_foundry", "gpt-4.1"), **{**_NO_KEYS, "azure_api_key": "azure-key"})

    assert isinstance(client, OpenAICompatibleClient)


def test_resolves_google_ai_studio_spec_to_its_own_client() -> None:
    client = resolve_client(make_spec("google_ai_studio", "gemini-3.8-flash"), **{**_NO_KEYS, "google_api_key": "google-key"})

    assert isinstance(client, GoogleAIStudioClient)


def test_unknown_provider_fails_loudly_naming_it_and_the_supported_ones() -> None:
    with pytest.raises(ValueError) as excinfo:
        resolve_client(make_spec("groq", "removed-model"), **_NO_KEYS)

    message = str(excinfo.value)
    assert "groq" in message
    for provider in ("google_ai_studio", "azure_ai_foundry"):
        assert provider in message
