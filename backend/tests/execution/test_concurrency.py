import asyncio

from evaluation.execution.concurrency import ConcurrencyLimitedClient, ProviderConcurrency
from tests.execution.conftest import BlockingClient, make_spec


async def _drive(client, spec, count):
    return [asyncio.create_task(client.complete(spec, "p", None, 0.0, 16)) for _ in range(count)]


async def test_per_provider_cap_limits_parallelism() -> None:
    release = asyncio.Event()
    inner = BlockingClient(release)
    limited = ConcurrencyLimitedClient(inner, ProviderConcurrency(default=2))
    spec = make_spec("azure_ai_foundry")

    tasks = await _drive(limited, spec, 5)
    await asyncio.sleep(0.05)
    assert inner.peak == 2

    release.set()
    await asyncio.gather(*tasks)


async def test_different_providers_run_in_parallel() -> None:
    release = asyncio.Event()
    inner = BlockingClient(release)
    limited = ConcurrencyLimitedClient(inner, ProviderConcurrency(limits={"azure_ai_foundry": 1, "google_ai_studio": 1}))

    tasks = [
        asyncio.create_task(limited.complete(make_spec("azure_ai_foundry"), "p", None, 0.0, 16)),
        asyncio.create_task(limited.complete(make_spec("google_ai_studio"), "p", None, 0.0, 16)),
    ]
    await asyncio.sleep(0.05)
    assert inner.peak == 2

    release.set()
    await asyncio.gather(*tasks)
