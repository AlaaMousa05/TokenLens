from datetime import datetime, timezone
from decimal import Decimal

from evaluation.contracts import CallStatus, ModelResponse, PriceSnapshot
from evaluation.cost import compute_call_cost

_CAPTURED_AT = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _snapshot(
    input_price: str,
    output_price: str,
    cached_price: str | None = None,
) -> PriceSnapshot:
    return PriceSnapshot(
        input_price_per_mtok=Decimal(input_price),
        output_price_per_mtok=Decimal(output_price),
        cached_input_price_per_mtok=Decimal(cached_price) if cached_price is not None else None,
        captured_at=_CAPTURED_AT,
    )


def _response(
    snapshot: PriceSnapshot,
    *,
    status: CallStatus = CallStatus.ok,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0,
) -> ModelResponse:
    return ModelResponse(
        output_text="",
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        reasoning_tokens=reasoning_tokens,
        latency_ms=0,
        attempts=1,
        status=status,
        tokens_estimated=False,
        prices_snapshot=snapshot,
    )


def test_zero_tokens_yield_zero_cost() -> None:
    snapshot = _snapshot("3.00", "15.00", cached_price="0.30")
    response = _response(snapshot)

    breakdown = compute_call_cost(response)

    assert breakdown.input_cost == Decimal("0.000000")
    assert breakdown.cached_cost == Decimal("0.000000")
    assert breakdown.output_cost == Decimal("0.000000")
    assert breakdown.reasoning_cost == Decimal("0.000000")
    assert breakdown.total_cost == Decimal("0.000000")


def test_failed_call_with_no_reported_tokens_costs_nothing() -> None:
    snapshot = _snapshot("3.00", "15.00")
    response = _response(snapshot, status=CallStatus.failed)

    breakdown = compute_call_cost(response)

    assert breakdown.total_cost == Decimal("0.000000")


def test_failed_call_is_still_charged_for_tokens_it_actually_reports() -> None:
    snapshot = _snapshot("3.00", "15.00")
    response = _response(snapshot, status=CallStatus.failed, input_tokens=1_000_000)

    breakdown = compute_call_cost(response)

    assert breakdown.input_cost == Decimal("3.000000")
    assert breakdown.total_cost == Decimal("3.000000")


def test_cached_tokens_use_cached_price_not_input_price() -> None:
    snapshot = _snapshot("3.00", "15.00", cached_price="0.30")
    response = _response(snapshot, cached_tokens=1_000_000)

    breakdown = compute_call_cost(response)

    assert breakdown.cached_cost == Decimal("0.300000")
    assert breakdown.input_cost == Decimal("0.000000")
    assert breakdown.total_cost == Decimal("0.300000")


def test_cached_tokens_fall_back_to_input_price_when_no_cached_price() -> None:
    snapshot = _snapshot("3.00", "15.00", cached_price=None)
    response = _response(snapshot, cached_tokens=1_000_000)

    breakdown = compute_call_cost(response)

    assert breakdown.cached_cost == Decimal("3.000000")
    assert breakdown.total_cost == Decimal("3.000000")


def test_reasoning_tokens_billed_at_output_rate() -> None:
    snapshot = _snapshot("3.00", "15.00")
    response = _response(snapshot, reasoning_tokens=1_000_000)

    breakdown = compute_call_cost(response)

    assert breakdown.reasoning_cost == Decimal("15.000000")
    assert breakdown.output_cost == Decimal("0.000000")
    assert breakdown.total_cost == Decimal("15.000000")


def test_decimal_arithmetic_does_not_drift_where_float_would() -> None:
    # Classic float trap: 0.1 + 0.2 != 0.3 in binary floating point.
    assert 0.1 + 0.2 != 0.3

    snapshot = _snapshot("0.1", "0.2")
    response = _response(snapshot, input_tokens=1_000_000, output_tokens=1_000_000)

    breakdown = compute_call_cost(response)

    assert breakdown.input_cost == Decimal("0.100000")
    assert breakdown.output_cost == Decimal("0.200000")
    assert breakdown.total_cost == Decimal("0.300000")
