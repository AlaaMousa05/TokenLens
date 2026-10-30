
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class ModelSpec(BaseModel):

    provider: str
    model_name: str = Field(description="API-facing model identifier.")
    display_name: str = Field(description="Human-readable name for the UI.")
    context_window: int = Field(description="Max input plus output tokens.")
    input_price_per_mtok: Decimal = Field(description="Current published input price.")
    output_price_per_mtok: Decimal = Field(description="Current published output price.")
    cached_input_price_per_mtok: Decimal | None = Field(default=None, description="Cached input price; None if no discount.")
    pricing_notes: str = Field(description="Caveats, e.g. tiered or promotional pricing.")
    is_active: bool = Field(description="Selectable for new evaluation runs.")
    reasoning_level: str | None = Field(
        default=None,
        description="Per-model reasoning/thinking effort; adapter maps it to the provider's vocabulary. None uses the adapter default.",
    )
    request_timeout_seconds: float | None = Field(
        default=None,
        description="Per-model request deadline in seconds; slow models need longer. None uses the adapter default.",
    )


class PriceSnapshot(BaseModel):

    input_price_per_mtok: Decimal = Field(description="Input price at call time.")
    output_price_per_mtok: Decimal = Field(description="Output price at call time.")
    cached_input_price_per_mtok: Decimal | None = Field(default=None, description="Cached input price at call time, if any.")
    captured_at: datetime = Field(description="When this snapshot was frozen.")


class CallStatus(str, Enum):
    ok = "ok"
    failed = "failed"


class ModelResponse(BaseModel):

    output_text: str = Field(description="Empty string on failure.")
    input_tokens: int = Field(default=0, description="Billed input tokens.")
    output_tokens: int = Field(default=0, description="Billed output tokens.")
    cached_tokens: int = Field(default=0, description="Cached-rate tokens, not output rate.")
    reasoning_tokens: int = Field(default=0, description="Billed separately from output.")
    latency_ms: int = Field(description="Wall-clock request to response.")
    attempts: int = Field(description="Attempts including retries.")
    status: CallStatus
    error_message: str | None = Field(default=None, description="Set only when status is failed.")
    tokens_estimated: bool = Field(description="True if counts are local estimates, not provider-reported.")
    prices_snapshot: PriceSnapshot


class ModelClient(ABC):

    @abstractmethod
    async def complete(
        self,
        spec: ModelSpec,
        prompt: str,
        system_prompt: str | None,
        temperature: float,
        max_output_tokens: int,
    ) -> ModelResponse:

        raise NotImplementedError
