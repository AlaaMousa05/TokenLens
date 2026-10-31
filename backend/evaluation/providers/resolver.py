

from collections.abc import Callable

from evaluation.contracts import ModelClient, ModelSpec
from evaluation.providers.google_ai_studio import GoogleAIStudioClient
from evaluation.providers.openai_compatible import DEFAULT_REASONING_EFFORT, OpenAICompatibleClient

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"


def resolve_client(
    spec: ModelSpec,
    *,
    groq_api_key: str | None,
    nvidia_api_key: str | None,
    google_api_key: str | None,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
) -> ModelClient:
   
    factories: dict[str, Callable[[], ModelClient]] = {
        "groq": lambda: OpenAICompatibleClient(
            base_url=GROQ_BASE_URL, api_key=groq_api_key, reasoning_effort=reasoning_effort
        ),
        "nvidia_nim": lambda: OpenAICompatibleClient(
            base_url=NVIDIA_NIM_BASE_URL, api_key=nvidia_api_key, reasoning_effort=reasoning_effort
        ),
        "google_ai_studio": lambda: GoogleAIStudioClient(api_key=google_api_key),
    }

    factory = factories.get(spec.provider)
    if factory is None:
        supported = ", ".join(sorted(factories))
        raise ValueError(f"Unsupported provider '{spec.provider}'. Supported providers: {supported}.")
    return factory()
