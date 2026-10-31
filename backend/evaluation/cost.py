from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from evaluation.contracts import ModelResponse

_ONE_MILLION = Decimal("1000000")
_SIX_DECIMAL_PLACES = Decimal("0.000001")


@dataclass(frozen=True)
class CallCostBreakdown:
    """USD cost of one model call, split by the token category it was billed under."""

    input_cost: Decimal
    cached_cost: Decimal
    output_cost: Decimal
    reasoning_cost: Decimal
    total_cost: Decimal


def compute_call_cost(response: ModelResponse) -> CallCostBreakdown:

    snapshot = response.prices_snapshot
    cached_price = snapshot.cached_input_price_per_mtok
    if cached_price is None:
        cached_price = snapshot.input_price_per_mtok

    input_cost = _token_cost(response.input_tokens, snapshot.input_price_per_mtok)
    cached_cost = _token_cost(response.cached_tokens, cached_price)
    output_cost = _token_cost(response.output_tokens, snapshot.output_price_per_mtok)
    reasoning_cost = _token_cost(response.reasoning_tokens, snapshot.output_price_per_mtok)
    total_cost = _quantize(input_cost + cached_cost + output_cost + reasoning_cost)

    return CallCostBreakdown(
        input_cost=input_cost,
        cached_cost=cached_cost,
        output_cost=output_cost,
        reasoning_cost=reasoning_cost,
        total_cost=total_cost,
    )


def _token_cost(token_count: int, price_per_mtok: Decimal) -> Decimal:
    return _quantize((Decimal(token_count) / _ONE_MILLION) * price_per_mtok)


def _quantize(amount: Decimal) -> Decimal:
    return amount.quantize(_SIX_DECIMAL_PLACES, rounding=ROUND_HALF_UP)
