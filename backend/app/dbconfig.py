from typing import Any
import logging

from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger("uvicorn.error.tokenlens")

class Base(DeclarativeBase):
    pass


engine: Any = None
SessionLocal: Any = None


def _ensure_session_factory() -> None:
    global engine, SessionLocal
    if SessionLocal is None:
        from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
        from app.config import settings

        engine = create_async_engine(settings.database_url, pool_pre_ping=True)
        SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def get_engine():
    _ensure_session_factory()
    return engine


async def get_db_session():
    _ensure_session_factory()
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def init_all_tables() -> None:
    _ensure_session_factory()
    # Import model modules so they are registered on Base.metadata.
    from app.models import entities  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await ensure_run_update_version()


async def ensure_run_update_version() -> None:
    """Apply the additive live-update column to databases created before it existed."""
    from sqlalchemy import inspect, text

    _ensure_session_factory()

    def has_column(conn):
        inspector = inspect(conn)
        if not inspector.has_table("runs"):
            raise RuntimeError("The runs table is missing; start the API to initialize the database.")
        return any(column["name"] == "update_version" for column in inspector.get_columns("runs"))

    async with engine.connect() as conn:
        if await conn.run_sync(has_column):
            return

    async with engine.begin() as conn:
        dialect = conn.dialect.name
        if dialect == "postgresql":
            await conn.execute(text("SELECT pg_advisory_xact_lock(746251839)"))
        elif dialect == "sqlite":
            await conn.execute(text("BEGIN IMMEDIATE"))
        else:
            raise RuntimeError(f"Automatic run update migration is unsupported for database dialect {dialect}.")
        if not await conn.run_sync(has_column):
            await conn.execute(text("ALTER TABLE runs ADD COLUMN update_version BIGINT NOT NULL DEFAULT 0"))
            logger.info("Added run update version column")
