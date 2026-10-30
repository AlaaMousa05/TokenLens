from decimal import Decimal

import pytest

from evaluation.contracts import ModelSpec


def make_spec(
    provider: str,
    model_name: str,
    reasoning_level: str | None = None,
    request_timeout_seconds: float | None = None,
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
    )


@pytest.fixture
def groq_spec() -> ModelSpec:
    return make_spec("groq", "openai/gpt-oss-120b")


@pytest.fixture
def nvidia_spec() -> ModelSpec:
    return make_spec("nvidia_nim", "openai/gpt-oss-20b")


@pytest.fixture
def gemini_spec() -> ModelSpec:
    return make_spec("google_ai_studio", "gemini-3.8-flash", reasoning_level="low")
