from typing import Any

from sqlalchemy.orm import DeclarativeBase


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
