"""FastAPI application entrypoint for the TokenLens backend."""

from contextlib import asynccontextmanager
import logging
from time import perf_counter

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from starlette.types import ASGIApp, Message, Receive, Scope, Send

import app.dbconfig as dbconfig
from app.config import settings
from app.controllers.auth_controller import router as auth_router
from app.controllers.dataset_controller import router as dataset_router
from app.controllers.model_controller import router as model_router
from app.controllers.rubric_controller import router as rubric_router
from app.controllers.run_controller import router as run_router
from app.controllers.user_controller import router as user_router
from app.dbconfig import get_engine, init_all_tables
from evaluation.judging.seed import seed_default_data
from evaluation.registry import seed_models


logger = logging.getLogger("uvicorn.error.tokenlens")


class RequestLoggingMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = perf_counter()
        status_code = None

        async def send_with_status(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_status)
        except Exception:
            self._log(scope, status_code or 500, started, failed=True)
            raise
        else:
            self._log(scope, status_code or 500, started, failed=False)

    @staticmethod
    def _log(scope: Scope, status_code: int, started: float, failed: bool) -> None:
        route = scope.get("route")
        route_path = getattr(route, "path_format", None) or "<unmatched>"
        method = scope.get("method", "")
        if method not in {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}:
            method = "OTHER"
        level = logging.ERROR if failed or status_code >= 500 else (
            logging.WARNING if status_code >= 400 else logging.INFO
        )
        logger.log(
            level,
            "HTTP request completed method=%s route=%s status=%s duration_ms=%.1f failed=%s",
            method, route_path, status_code, (perf_counter() - started) * 1000, failed,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API starting")
    try:
        engine = get_engine()
        await init_all_tables()
        async with dbconfig.SessionLocal() as session:
            await seed_models(session)
            await seed_default_data(session)
    except Exception:
        logger.error("API startup failed")
        raise
    logger.info("API startup complete")
    try:
        yield
    finally:
        logger.info("API shutting down")
        try:
            await engine.dispose()
        except Exception:
            logger.error("API shutdown failed")
            raise
        logger.info("API shutdown complete")


app = FastAPI(title="TokenLens API", lifespan=lifespan)
cors_allowed_origins = [
    origin.strip()
    for origin in settings.cors_allowed_origins.split(",")
    if origin.strip()
]
allow_all_origins = "*" in cors_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else cors_allowed_origins,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
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
