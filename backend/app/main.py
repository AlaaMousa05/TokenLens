"""FastAPI application entrypoint for the TokenLens backend."""

from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy import text

from app.config import settings
from app.controllers.auth_controller import router as auth_router
from app.controllers.dataset_controller import router as dataset_router
from app.controllers.model_controller import router as model_router
from app.controllers.rubric_controller import router as rubric_router
from app.controllers.run_controller import router as run_router
from app.controllers.user_controller import router as user_router
from app.dbconfig import get_engine, init_all_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    await init_all_tables()
    yield
    await engine.dispose()


app = FastAPI(title="TokenLens API", lifespan=lifespan)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(model_router)
app.include_router(dataset_router)
app.include_router(rubric_router)
app.include_router(run_router)


@app.get(
    "/health",
    summary="Health check",
    responses={
        200: {
            "description": "Service health with database/redis checks. Status can be ok or degraded.",
            "content": {
                "application/json": {
                    "examples": {
                        "ok": {
                            "summary": "All checks passed",
                            "value": {"status": "ok", "checks": {"database": "ok", "redis": "ok"}},
                        },
                        "degraded": {
                            "summary": "One dependency failed",
                            "value": {
                                "status": "degraded",
                                "checks": {"database": "ok", "redis": "error: connection failed"},
                            },
                        },
                    }
                }
            },
        }
    },
)
async def health() -> dict:
    engine = get_engine()
    checks: dict[str, str] = {}
    status = "ok"

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc: 
        checks["database"] = f"error: {exc}"
        status = "degraded"

    redis_client = redis.from_url(settings.redis_url)
    try:
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception as exc: 
        checks["redis"] = f"error: {exc}"
        status = "degraded"
    finally:
        await redis_client.aclose()

    return {"status": status, "checks": checks}
