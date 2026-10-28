"""FastAPI application entrypoint for the TokenLens backend."""

from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(title="TokenLens API", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
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
