import asyncio
import logging

from sqlalchemy.ext.asyncio import create_async_engine

from silo import config
from silo.database import BaseDatabaseObject

logger = logging.getLogger()


async def migrate_tables() -> None:
    logger.info("Starting to migrate")

    engine = create_async_engine(config.database_uri)
    async with engine.begin() as conn:
        await conn.run_sync(BaseDatabaseObject.metadata.create_all)

    logger.info("Done migrating")


if __name__ == "__main__":
    asyncio.run(migrate_tables())
