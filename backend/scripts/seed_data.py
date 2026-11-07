"""Seeds the default demo dataset and rubric. No API calls.

    python -m scripts.seed_data
"""

import asyncio

import app.dbconfig as dbconfig
from evaluation.judging.seed import seed_default_data


async def main() -> None:
    dbconfig._ensure_session_factory()
    async with dbconfig.SessionLocal() as session:
        await seed_default_data(session)


if __name__ == "__main__":
    asyncio.run(main())
