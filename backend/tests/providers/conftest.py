from decimal import Decimal

import pytest

from evaluation.contracts import ModelSpec


def make_spec(
    provider: str,
    model_name: str,
    reasoning_level: str | None = None,
    request_timeout_seconds: float | None = None,
    uses_max_completion_tokens: bool = False,
    accepts_custom_temperature: bool = True,
    response_format: str | None = None,
) -> ModelSpec:
    return ModelSpec(
        provider=provider,
        model_name=model_name,
        display_name=f"{model_name} ({provider})",
        context_window=131072,
        input_price_per_mtok=Decimal("1.00"),
        output_price_per_mtok=Decimal("2.00"),
        pricing_notes="test fixture",
        is_active=True,
        reasoning_level=reasoning_level,
        request_timeout_seconds=request_timeout_seconds,
        uses_max_completion_tokens=uses_max_completion_tokens,
        accepts_custom_temperature=accepts_custom_temperature,
        response_format=response_format,
    )


@pytest.fixture
def azure_spec() -> ModelSpec:
    return make_spec("azure_ai_foundry", "gpt-4.1")


@pytest.fixture
def gemini_spec() -> ModelSpec:
    return make_spec("google_ai_studio", "gemini-3.8-flash", reasoning_level="low")
