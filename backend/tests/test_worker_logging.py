import asyncio
import logging
import os
import subprocess
import sys
import uuid
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from evaluation.contracts import CallStatus
from evaluation.judging.verdict import Judgment, JudgmentStatus
from tests.execution.conftest import failed_response, make_spec, ok_response


@pytest.fixture
def worker(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret")
    from worker import main

    return main


def test_worker_lifecycle_hooks(worker, caplog):
    with caplog.at_level(logging.INFO, logger=worker.logger.name):
        asyncio.run(worker.WorkerSettings.on_startup({}))
        asyncio.run(worker.WorkerSettings.on_shutdown({}))
    assert "Worker started pid=" in caplog.text
    assert "Worker stopped pid=" in caplog.text


def test_worker_logs_are_visible_with_arq_default_configuration():
    env = os.environ.copy()
    env.update(
        DATABASE_URL="sqlite+aiosqlite:///:memory:",
        REDIS_URL="redis://localhost:6379/0",
        JWT_SECRET_KEY="test-secret",
    )
    script = """
import asyncio
import logging.config
from arq.logs import default_log_config
from worker.main import on_startup
logging.config.dictConfig(default_log_config(False))
asyncio.run(on_startup({}))
"""
    result = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, check=True)
    assert "Worker started pid=" in result.stderr


@pytest.mark.parametrize("response", [ok_response(), failed_response("sensitive provider error")])
def test_model_call_logs_status_without_content(worker, caplog, response):
    run = SimpleNamespace(id=uuid.uuid4(), temperature=Decimal("0"))
    model = SimpleNamespace(id=uuid.uuid4())
    item = SimpleNamespace(id=uuid.uuid4(), input_prompt="private prompt")
    session = SimpleNamespace(add=MagicMock(), flush=AsyncMock())
    client = SimpleNamespace(complete=AsyncMock(return_value=response))

    with caplog.at_level(logging.INFO, logger=worker.logger.name):
        result = asyncio.run(worker._generate_and_persist_result(
            session, client, make_spec("test"), run, model, item, 0, "private policy"
        ))

    assert f"run_id={run.id}" in caplog.text
    assert f"status={response.status.value}" in caplog.text
    assert "Model call started" in caplog.text
    assert "Model call finished" in caplog.text
    assert "private prompt" not in caplog.text
    assert "private policy" not in caplog.text
    assert "sensitive provider error" not in caplog.text
    assert result.status == (worker.ResultStatus.OK if response.status is CallStatus.ok else worker.ResultStatus.FAILED)
    if response.status is CallStatus.failed:
        assert any(record.levelno == logging.WARNING for record in caplog.records)


def test_failed_judgment_logs_warning_without_response(worker, caplog):
    judgment = Judgment(
        status=JudgmentStatus.failed, rubric_name="test", rubric_version=1,
        attempts=2, error_message="private judge response",
    )
    judge = SimpleNamespace(score=AsyncMock(return_value=judgment))
    result = SimpleNamespace(id=uuid.uuid4(), run_id=uuid.uuid4(), output_text="private answer")
    session = SimpleNamespace(add=MagicMock())
    recorder = SimpleNamespace(total_cost=Decimal("0"))
    with caplog.at_level(logging.INFO, logger=worker.logger.name):
        asyncio.run(worker._score_result(
            session, judge, recorder, uuid.uuid4(), result, False, "policy", "question", "reference"
        ))
    assert "Judging started" in caplog.text
    assert "status=failed" in caplog.text
    assert any(record.levelno == logging.WARNING for record in caplog.records)
    assert "private" not in caplog.text
    session.add.assert_called_once()


@pytest.mark.parametrize("fail", [False, True])
def test_evaluation_job_logs_outcome_and_preserves_status(worker, caplog, fail):
    run_id = uuid.uuid4()
    run = SimpleNamespace(status=worker.RunStatus.QUEUED, total_cost_usd=Decimal("0"), error_message=None)
    session = MagicMock()
    session.get = AsyncMock(return_value=run)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    execute = AsyncMock(side_effect=ValueError("private error") if fail else None, return_value=Decimal("1"))

    async def invoke():
        with patch.object(worker.dbconfig, "_ensure_session_factory"), \
             patch.object(worker.dbconfig, "SessionLocal", return_value=session), \
             patch.object(worker, "_load_run_context", new=AsyncMock(return_value=object())), \
             patch.object(worker, "_run_models", new=execute):
            await worker.run_evaluation({"job_id": "job-1"}, str(run_id))

    with caplog.at_level(logging.INFO, logger=worker.logger.name):
        if fail:
            with pytest.raises(ValueError):
                asyncio.run(invoke())
        else:
            asyncio.run(invoke())
    assert f"run_id={run_id}" in caplog.text
    assert "job_id=job-1" in caplog.text
    assert "Evaluation started" in caplog.text
    assert ("Evaluation failed" if fail else "Evaluation completed") in caplog.text
    assert "private error" not in caplog.text
    assert run.status == (worker.RunStatus.FAILED if fail else worker.RunStatus.COMPLETED)
