from evaluation.contracts import CallStatus
from evaluation.execution.fanout import fan_out
from tests.execution.conftest import CountingClient, MappingClient, failed_response, make_spec, ok_response


async def test_one_model_failing_does_not_cancel_the_others() -> None:
    specs = [make_spec("azure_ai_foundry", "fast"), make_spec("azure_ai_foundry", "broken"), make_spec("azure_ai_foundry", "slow")]
    client = MappingClient(
        {
            "fast": ok_response(),
            "broken": failed_response("azure returned HTTP 400 for broken: bad"),
            "slow": ok_response(),
        }
    )

    results = await fan_out(client, specs, "p", max_output_tokens=16)

    assert [r.spec.model_name for r in results] == ["fast", "broken", "slow"]
    assert [r.responses[0].status for r in results] == [CallStatus.ok, CallStatus.failed, CallStatus.ok]


async def test_repeats_are_separate_calls_and_results() -> None:
    inner = CountingClient(ok_response())
    specs = [make_spec("azure_ai_foundry", "m")]

    results = await fan_out(inner, specs, "p", max_output_tokens=16, repeats=3)

    assert len(results) == 1
    assert len(results[0].responses) == 3
    assert inner.calls == 3
