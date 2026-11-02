"""Resolves a ModelSpec's provider string to a configured ModelClient.

Adding a model on an already-supported provider is a new row in the
registry, not a code change here.
"""

from collections.abc import Callable

from evaluation.contracts import ModelClient, ModelSpec
from evaluation.providers.google_ai_studio import GoogleAIStudioClient
from evaluation.providers.openai_compatible import OpenAICompatibleClient

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"


def resolve_client(
    spec: ModelSpec,
    *,
    groq_api_key: str | None,
    nvidia_api_key: str | None,
    google_api_key: str | None,
) -> ModelClient:
    """Build the ModelClient serving spec.provider, injected with its API key.

    Per-call settings (reasoning level, timeout) travel on the spec, not
    through here. Raises ValueError naming the unsupported provider and the
    supported ones if spec.provider matches none of them.
    """
    factories: dict[str, Callable[[], ModelClient]] = {
        "groq": lambda: OpenAICompatibleClient(base_url=GROQ_BASE_URL, api_key=groq_api_key),
        "nvidia_nim": lambda: OpenAICompatibleClient(base_url=NVIDIA_NIM_BASE_URL, api_key=nvidia_api_key),
        "google_ai_studio": lambda: GoogleAIStudioClient(api_key=google_api_key),
    }

    factory = factories.get(spec.provider)
    if factory is None:
        supported = ", ".join(sorted(factories))
        raise ValueError(f"Unsupported provider '{spec.provider}'. Supported providers: {supported}.")
    return factory()
