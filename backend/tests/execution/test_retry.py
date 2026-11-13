import random

from evaluation.contracts import CallStatus
from evaluation.execution.retry import RetryingClient, RetryPolicy
from tests.execution.conftest import (
    RecordingSleep,
    ScriptedClient,
    failed_response,
    make_spec,
    ok_response,
)

_SPEC = make_spec("azure_ai_foundry")
_POLICY = RetryPolicy(max_attempts=3, base_delay_seconds=0.5, max_delay_seconds=8.0, max_elapsed_seconds=30.0)


def _client(inner, *, policy=_POLICY, sleep=None, monotonic=None):
    return RetryingClient(
        inner,
        policy,
        sleep=sleep or RecordingSleep(),
        rng=random.Random(0),
        monotonic=monotonic or (lambda: 0.0),
    )


async def _call(client):
    return await client.complete(_SPEC, "p", None, 0.0, 16)


async def test_succeeds_on_second_attempt() -> None:
    inner = ScriptedClient([failed_response("Request to azure timed out after 30.0s."), ok_response()])
    response = await _call(_client(inner))

    assert response.status is CallStatus.ok
    assert response.attempts == 2
    assert inner.calls == 2


async def test_exhausts_retries_and_returns_last_failure() -> None:
    inner = ScriptedClient([failed_response("azure rate limit (429) hit for m.")])
    response = await _call(_client(inner))

    assert response.status is CallStatus.failed
    assert response.attempts == 3
    assert inner.calls == 3


async def test_client_error_is_not_retried() -> None:
    inner = ScriptedClient([failed_response("azure returned HTTP 400 for m: bad request"), ok_response()])
    response = await _call(_client(inner))

    assert response.status is CallStatus.failed
    assert response.attempts == 1
    assert inner.calls == 1


async def test_retry_after_is_honored_over_backoff() -> None:
    inner = ScriptedClient([failed_response("azure rate limit (429) hit for m.", retry_after_seconds=7.0), ok_response()])
    sleep = RecordingSleep()
    response = await _call(_client(inner, sleep=sleep))

    assert response.status is CallStatus.ok
    assert sleep.delays == [7.0]


async def test_backoff_delay_stays_within_the_cap() -> None:
    inner = ScriptedClient([failed_response("azure returned HTTP 503 for m: busy"), ok_response()])
    sleep = RecordingSleep()
    await _call(_client(inner, sleep=sleep))

    assert len(sleep.delays) == 1
    assert 0.0 <= sleep.delays[0] <= _POLICY.base_delay_seconds


async def test_total_elapsed_ceiling_stops_retrying_early() -> None:
    inner = ScriptedClient([failed_response("azure rate limit (429) hit for m.")])
    clock = iter([0.0, 100.0, 100.0, 100.0])
    policy = RetryPolicy(max_attempts=5, max_elapsed_seconds=30.0)
    response = await _call(_client(inner, policy=policy, monotonic=lambda: next(clock)))

    assert response.status is CallStatus.failed
    assert inner.calls == 1
