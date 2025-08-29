from silo.database.models import Base
from silo.database import async_engine


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
