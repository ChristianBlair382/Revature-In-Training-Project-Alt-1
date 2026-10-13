# Run with: python -m scripts.seed_permissions
# From: backend/ with venv active

import asyncio

from app.database import AsyncSessionLocal
from scripts.seed_tables import seed_permissions


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed_permissions(session)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
