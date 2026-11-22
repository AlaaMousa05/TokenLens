import json
import unittest
import uuid
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.controllers.run_controller import stream_run_events
from app.dbconfig import Base
from app.models.entities import Judgment, Result, ResultStatus, Run, RunStatus
from evaluation.contracts import CallStatus
from worker.main import _run_models


class LiveRunTests(unittest.IsolatedAsyncioTestCase):
    async def test_stream_reports_results_judgments_and_terminal_status(self):
        run_id = uuid.uuid4()
        user = SimpleNamespace(id=uuid.uuid4())
        initial_session = SimpleNamespace(rollback=AsyncMock())
        stream_session = MagicMock()
        stream_session.scalar = AsyncMock(side_effect=[0, 0, 1, 0, 1, 1])
        context_manager = MagicMock()
        context_manager.__aenter__ = AsyncMock(return_value=stream_session)
        context_manager.__aexit__ = AsyncMock(return_value=None)
        runs = [SimpleNamespace(run=SimpleNamespace(status=status, total_cost_usd=Decimal("0.01"))) for status in (
            RunStatus.QUEUED, RunStatus.RUNNING, RunStatus.RUNNING, RunStatus.COMPLETED,
        )]
        with patch("app.controllers.run_controller.get_user_run", new=AsyncMock(side_effect=runs)), \
             patch("app.controllers.run_controller.dbconfig.SessionLocal", return_value=context_manager), \
             patch("app.controllers.run_controller.asyncio.sleep", new=AsyncMock()):
            response = await stream_run_events(run_id, user, initial_session)
            frames = [frame async for frame in response.body_iterator]

        updates = [json.loads(frame.split("data: ", 1)[1]) for frame in frames]
        self.assertEqual([(event["status"], event["result_count"], event["judgment_count"]) for event in updates], [
            ("running", 0, 0), ("running", 1, 0), ("completed", 1, 1),
        ])
        self.assertTrue(all(event["run_id"] == str(run_id) for event in updates))
        initial_session.rollback.assert_awaited_once()

    async def test_stream_rejects_another_users_run(self):
        with patch("app.controllers.run_controller.get_user_run", new=AsyncMock(return_value=None)):
            with self.assertRaises(HTTPException) as error:
                await stream_run_events(uuid.uuid4(), SimpleNamespace(id=uuid.uuid4()), MagicMock())
        self.assertEqual(error.exception.status_code, 404)

    async def test_stream_reads_committed_changes_from_database(self):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        user_id, run_id, model_id, item_id, judge_id, result_id = [uuid.uuid4() for _ in range(6)]
        async with sessions() as session:
            session.add(Run(
                id=run_id, user_id=user_id, dataset_id=uuid.uuid4(), rubric_id=uuid.uuid4(),
                judge_model_id=judge_id, name="run", repeats=1, temperature=0, swap_order=False,
                status=RunStatus.RUNNING, total_cost_usd=0,
            ))
            await session.commit()
        try:
            with patch("app.controllers.run_controller.dbconfig.SessionLocal", sessions), \
                 patch("app.controllers.run_controller.asyncio.sleep", new=AsyncMock()):
                async with sessions() as initial_session:
                    response = await stream_run_events(run_id, SimpleNamespace(id=user_id), initial_session)
                    stream = response.body_iterator
                    first = json.loads((await anext(stream)).split("data: ", 1)[1])
                    async with sessions() as session:
                        session.add(Result(
                            id=result_id, run_id=run_id, item_id=item_id, model_id=model_id, repeat_index=0,
                            output_text="response", input_tokens=2, output_tokens=3, latency_ms=20,
                            cost_usd=Decimal("0.01"), status=ResultStatus.OK, attempts=1,
                        ))
                        await session.commit()
                    second = json.loads((await anext(stream)).split("data: ", 1)[1])
                    async with sessions() as session:
                        session.add(Judgment(
                            result_id=result_id, judge_model_id=judge_id, order_variant=0,
                            score=4, criteria_scores={}, reasoning="", judge_cost_usd=Decimal("0.001"),
                        ))
                        run = await session.get(Run, run_id)
                        run.status = RunStatus.COMPLETED
                        await session.commit()
                    last = json.loads((await anext(stream)).split("data: ", 1)[1])
                    with self.assertRaises(StopAsyncIteration):
                        await anext(stream)
            self.assertEqual((first["result_count"], second["result_count"]), (0, 1))
            self.assertEqual((last["status"], last["judgment_count"]), ("completed", 1))
        finally:
            await engine.dispose()

    async def test_answer_is_committed_before_judging(self):
        run = SimpleNamespace(id=uuid.uuid4(), temperature=Decimal("0"), swap_order=False, repeats=1, total_cost_usd=Decimal("0"))
        model = SimpleNamespace(id=uuid.uuid4(), model_name="candidate")
        context = SimpleNamespace(
            run=run, dataset=SimpleNamespace(description=""),
            items=[SimpleNamespace(id=uuid.uuid4(), input_prompt="question", expected_output="answer")],
            model_rows=[model], judge_model_row=SimpleNamespace(id=uuid.uuid4(), model_name="judge"), rubric_row=object(),
        )
        response = SimpleNamespace(status=CallStatus.ok, output_text="model response")
        client = SimpleNamespace(complete=AsyncMock(return_value=response))
        session = MagicMock()
        session.flush = AsyncMock()
        session.get = AsyncMock(return_value=run)
        session.commit = AsyncMock()

        async def judge(*args):
            self.assertEqual(session.commit.await_count, 1)
            self.assertEqual(run.total_cost_usd, Decimal("0.02"))
            return []

        with patch("worker.main._build_client", return_value=client), \
             patch("worker.main.get_model_by_name", side_effect=lambda name: name), \
             patch("worker.main.ensure_judge_not_judged"), \
             patch("worker.main._build_rubric", return_value=object()), \
             patch("worker.main._result_fields", return_value={"cost_usd": Decimal("0.02")}), \
             patch("worker.main._judge_calls", side_effect=judge), \
             patch("worker.main._add_judgments"):
            cost = await _run_models(session, context)
        self.assertEqual(cost, Decimal("0.02"))
        self.assertEqual(session.commit.await_count, 2)
