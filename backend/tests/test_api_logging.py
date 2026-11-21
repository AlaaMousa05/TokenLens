import logging
import uuid
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import main
from app.services import run_service


def test_http_logs_route_template_and_excludes_request_data(caplog):
    app = FastAPI()
    app.add_middleware(main.RequestLoggingMiddleware)

    @app.post("/items/{item_id}")
    async def item(item_id: str):
        return {"result": "response-secret"}

    @app.get("/fail/{item_id}")
    async def fail(item_id: str):
        raise RuntimeError("exception-secret")

    with caplog.at_level(logging.INFO, logger="uvicorn.error.tokenlens"):
        client = TestClient(app, raise_server_exceptions=False)
        assert client.post(
            "/items/path-secret?token=query-secret",
            headers={"Authorization": "Bearer header-secret"},
            json={"prompt": "body-secret"},
        ).status_code == 200
        assert client.get("/unknown/path-secret?token=query-secret").status_code == 404
        assert client.get("/fail/path-secret").status_code == 500

    messages = [record.getMessage() for record in caplog.records]
    assert len(messages) == 3
    assert "method=POST route=/items/{item_id} status=200" in messages[0]
    assert "route=<unmatched> status=404" in messages[1]
    assert "route=/fail/{item_id} status=500" in messages[2]
    assert "failed=True" in messages[2]
    assert all("secret" not in message for message in messages)
    assert [r.levelno for r in caplog.records] == [logging.INFO, logging.WARNING, logging.ERROR]


@pytest.mark.asyncio
async def test_lifespan_logs_startup_and_shutdown(monkeypatch, caplog):
    engine = SimpleNamespace(dispose=AsyncMock())
    session = object()

    @asynccontextmanager
    async def session_factory():
        yield session

    monkeypatch.setattr(main, "get_engine", lambda: engine)
    monkeypatch.setattr(main, "init_all_tables", AsyncMock())
    monkeypatch.setattr(main.dbconfig, "SessionLocal", session_factory)
    monkeypatch.setattr(main, "seed_models", AsyncMock())
    monkeypatch.setattr(main, "seed_default_data", AsyncMock())
    with caplog.at_level(logging.INFO, logger="uvicorn.error.tokenlens"):
        async with main.lifespan(main.app):
            pass
    assert [r.getMessage() for r in caplog.records] == [
        "API starting", "API startup complete", "API shutting down", "API shutdown complete"
    ]
    engine.dispose.assert_awaited_once()


@pytest.mark.asyncio
async def test_lifespan_logs_startup_failure_without_exception_details(monkeypatch, caplog):
    monkeypatch.setattr(main, "get_engine", lambda: object())
    monkeypatch.setattr(main, "init_all_tables", AsyncMock(side_effect=RuntimeError("startup-secret")))
    with caplog.at_level(logging.INFO, logger="uvicorn.error.tokenlens"):
        with pytest.raises(RuntimeError, match="startup-secret"):
            async with main.lifespan(main.app):
                pass
    assert [r.getMessage() for r in caplog.records] == ["API starting", "API startup failed"]


@pytest.mark.asyncio
async def test_lifespan_logs_shutdown_failure_without_exception_details(monkeypatch, caplog):
    engine = SimpleNamespace(dispose=AsyncMock(side_effect=RuntimeError("shutdown-secret")))

    @asynccontextmanager
    async def session_factory():
        yield object()

    monkeypatch.setattr(main, "get_engine", lambda: engine)
    monkeypatch.setattr(main, "init_all_tables", AsyncMock())
    monkeypatch.setattr(main.dbconfig, "SessionLocal", session_factory)
    monkeypatch.setattr(main, "seed_models", AsyncMock())
    monkeypatch.setattr(main, "seed_default_data", AsyncMock())
    with caplog.at_level(logging.INFO, logger="uvicorn.error.tokenlens"):
        with pytest.raises(RuntimeError, match="shutdown-secret"):
            async with main.lifespan(main.app):
                pass
    assert [r.getMessage() for r in caplog.records] == [
        "API starting", "API startup complete", "API shutting down", "API shutdown failed"
    ]


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", ["success", "no_job", "error"])
async def test_run_enqueue_logging(monkeypatch, caplog, outcome):
    run_id = uuid.uuid4()
    run = SimpleNamespace(id=run_id)
    rubric = SimpleNamespace(criteria=[], scale_min=1, scale_max=5)
    session = MagicMock()
    session.scalar = AsyncMock(side_effect=[object(), 1, rubric, object()])
    session.scalars = AsyncMock(return_value=SimpleNamespace(all=lambda: [object()]))
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    monkeypatch.setattr(run_service, "Run", lambda **kwargs: run)
    monkeypatch.setattr(run_service, "RunModel", lambda **kwargs: object())
    monkeypatch.setattr(run_service, "validate_rubric_values", lambda *args: None)
    monkeypatch.setattr(run_service, "freeze_rubric", AsyncMock())
    enqueue = AsyncMock()
    if outcome == "error":
        enqueue.side_effect = RuntimeError("redis-secret")
    elif outcome == "no_job":
        enqueue.return_value = None
    else:
        enqueue.return_value = object()
    monkeypatch.setattr(run_service, "_get_redis_pool", AsyncMock(return_value=SimpleNamespace(enqueue_job=enqueue)))
    args = dict(
        session=session, user_id=uuid.uuid4(), name="private-name", dataset_id=uuid.uuid4(),
        rubric_id=uuid.uuid4(), model_ids=[uuid.uuid4()], judge_model_id=uuid.uuid4(),
        repeats=1, temperature=0.0, swap_order=False,
    )
    with caplog.at_level(logging.INFO, logger="uvicorn.error.tokenlens"):
        if outcome == "error":
            with pytest.raises(RuntimeError, match="redis-secret"):
                await run_service.create_run(**args)
        else:
            await run_service.create_run(**args)
    enqueue.assert_awaited_once_with("run_evaluation", str(run_id))
    messages = [r.getMessage() for r in caplog.records]
    expected = {"success": "Run enqueued", "no_job": "Run enqueue returned no job", "error": "Run enqueue failed"}
    assert len(messages) == 2
    assert all(str(run_id) in message for message in messages)
    assert expected[outcome] in messages[1]
    assert all("secret" not in message and "private-name" not in message for message in messages)
