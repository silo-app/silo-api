from collections.abc import AsyncGenerator

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from silo import config

connection_string = f"{config.postgres_database_uri}"

async_engine = create_async_engine(str(config.postgres_database_uri), echo=False, future=True)
local_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with local_session() as db:
        yield db