from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.database import async_get_db
from silo.database import models
from silo.schemas import PoolBase, PoolCreate, PoolRead

pool_router = APIRouter(tags=["Pool"])

@pool_router.get(
    "/pool/",
    summary="Get all Pools",
    response_model=list[PoolRead],
)
@pool_router.get(
    "/pool/{id}",
    summary="Get a specific Pool",
    response_model=PoolRead,
)
async def get_pools(session: AsyncSession = Depends(async_get_db), id: int | None = None) -> PoolRead | list[PoolRead]:
    if id is not None:
        result = await session.scalars(select(models.Pool).where(models.Pool.id == id))
        pool = result.one_or_none()

        if pool is not None:
            return PoolRead.model_validate(pool, from_attributes=True)
        
        raise HTTPException(status_code=404, detail=f"Pool {id} not found")

    result = await session.scalars(select(models.Pool))
    pools = result.all()

    return [PoolRead.model_validate(room, from_attributes=True) for room in pools]


@pool_router.post(
    "/pool/",
    summary="Add a new Pool",
    response_model=PoolRead,
    status_code=201,
)
async def new_pool(pool: PoolCreate, session: AsyncSession = Depends(async_get_db)) -> PoolRead:
    new_pool = models.Pool(**pool.model_dump())
    session.add(new_pool)
    await session.commit()
    return new_pool

@pool_router.put(
    "/pool/{id}",
    summary="Update an existing Pool",
    status_code=204,
)
async def update_pool(id: int, pool_update: PoolCreate, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.Pool).where(models.Pool.id == id))
    pool = result.one_or_none()
    if pool is None:
        raise HTTPException(404, detail="Pool not found")

    update_data = pool_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(pool, k, v)

    await session.commit()


@pool_router.delete(
    "/pool/{id}",
    summary="Delete a Pool",
    status_code=204,
)
async def delete_pool(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.Pool).where(models.Pool.id == id))
    pool = result.one_or_none()
    if pool is None:
        raise HTTPException(404, detail="Pool not found")

    await session.delete(pool)
    await session.commit()
