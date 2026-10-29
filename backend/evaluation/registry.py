"""Single source of truth for which models TokenLens compares and which model judges them.

Changing a model's identifier or price means editing this file only.
"""

from decimal import Decimal

from evaluation.contracts import ModelSpec

_GPT_OSS_120B = ModelSpec(
    provider="groq",
    model_name="openai/gpt-oss-120b",
    display_name="GPT-OSS 120B (Groq)",
    context_window=131072,
    input_price_per_mtok=Decimal("0.15"),
    output_price_per_mtok=Decimal("0.75"),
    cached_input_price_per_mtok=None,
    pricing_notes=(
        "Priced at Groq's published rate card, used as the single reference "
        "host for all three compared models since none has a single list "
        "price as an open-weight model. Served by Groq's free tier: 30 RPM, "
        "1000 RPD, 200K tokens/day shared across all models on the account."
    ),
    is_active=True,
)

_QWEN3_27B = ModelSpec(
    provider="groq",
    model_name="qwen/qwen3.8-27b",
    display_name="Qwen3.8 27B (Groq)",
    context_window=131072,
    input_price_per_mtok=Decimal("0.29"),
    output_price_per_mtok=Decimal("0.59"),
    cached_input_price_per_mtok=None,
    pricing_notes=(
        "Priced at Groq's published rate card, the same reference host used "
        "for the other compared models. Served by Groq's free tier: 30 RPM, "
        "1000 RPD, 200K tokens/day shared across all models on the account."
    ),
    is_active=True,
)

_GPT_OSS_20B = ModelSpec(
    provider="nvidia_nim",
    model_name="openai/gpt-oss-20b",
    display_name="GPT-OSS 20B (NVIDIA NIM)",
    context_window=131072,
    input_price_per_mtok=Decimal("0.05"),
    output_price_per_mtok=Decimal("0.20"),
    cached_input_price_per_mtok=None,
    pricing_notes=(
        "Priced at Groq's published rate card for this model, the same "
        "reference host used for the other compared models even though it "
        "is actually served by NVIDIA NIM here. Deliberately placed on NIM "
        "rather than Groq so it does not compete for Groq's shared daily "
        "token budget. Served by NVIDIA NIM's free tier: 40 RPM, 10000 RPD, "
        "per model."
    ),
    is_active=True,
)

_GEMINI_JUDGE = ModelSpec(
    provider="google_ai_studio",
    model_name="gemini-3.8-flash",
    display_name="Gemini 3.8 Flash (judge)",
    context_window=1_000_000,
    input_price_per_mtok=Decimal("0.30"),
    output_price_per_mtok=Decimal("2.50"),
    cached_input_price_per_mtok=Decimal("0.075"),
    pricing_notes=(
        "Priced at Google's own published Gemini API rate card, not the "
        "reference host used for the compared models. Excluded from the "
        "compared set to avoid a conflict of interest. Google AI Studio "
        "free tier (community-reported; Google no longer publishes "
        "per-model figures): roughly 10 RPM, 1500 RPD."
    ),
    is_active=True,
)

_COMPARED_MODELS: tuple[ModelSpec, ...] = (_GPT_OSS_120B, _QWEN3_27B, _GPT_OSS_20B)


def get_compared_models() -> list[ModelSpec]:
    """Active models eligible for a comparison run. Never includes the judge."""
    return [model for model in _COMPARED_MODELS if model.is_active]


def get_judge_model() -> ModelSpec:
    """The model that grades comparison runs, kept out of get_compared_models()."""
    return _GEMINI_JUDGE
