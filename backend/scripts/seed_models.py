"""Seeds the models table from the evaluation registry. No API calls.

    python -m scripts.seed_models
"""

import asyncio

import app.dbconfig as dbconfig
from evaluation.registry import seed_models


async def main() -> None:
    dbconfig._ensure_session_factory()
    async with dbconfig.SessionLocal() as session:
        await seed_models(session)


if __name__ == "__main__":
    asyncio.run(main())
