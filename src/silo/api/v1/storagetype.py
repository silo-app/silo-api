from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import StorageTypeCreate, StorageTypeRead

storage_type_router = APIRouter(
    tags=["StorageType"], dependencies=[Depends(require_permission())]
)


@storage_type_router.get(
    "/storagetype/",
    summary="Get all StorageTypes",
    response_model=list[StorageTypeRead],
)
@storage_type_router.get(
    "/storagetype/{id}",
    summary="Get a specific StorageType",
    response_model=StorageTypeRead,
)
async def get_storage_types(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> StorageTypeRead | list[StorageTypeRead]:
    if id is not None:
        result = await session.scalars(
            select(models.StorageType).where(models.StorageType.id == id)
        )
        storage_type = result.one_or_none()

        if storage_type is not None:
            return StorageTypeRead.model_validate(storage_type)

        raise HTTPException(status_code=404, detail=f"StorageType {id} not found")

    result = await session.scalars(select(models.StorageType))
    storage_types = result.all()

    return [
        StorageTypeRead.model_validate(storage_type, from_attributes=True)
        for storage_type in storage_types
    ]


@storage_type_router.post(
    "/storagetype/",
    summary="Add a new StorageType",
    response_model=StorageTypeRead,
    status_code=201,
)
async def new_storage_type(
    storage_type: StorageTypeCreate, session: AsyncSession = Depends(async_get_db)
) -> StorageTypeRead:
    new_storage_type = models.StorageType(**storage_type.model_dump())
    session.add(new_storage_type)
    await session.commit()
    return new_storage_type


@storage_type_router.put(
    "/storagetype/{id}",
    summary="Update an existing StorageType",
    status_code=204,
)
async def update_storage_type(
    id: int,
    storage_type_update: StorageTypeCreate,
    session: AsyncSession = Depends(async_get_db),
):
    result = await session.scalars(
        select(models.StorageType).where(models.StorageType.id == id)
    )
    storage_type = result.first()
    if storage_type is None:
        raise HTTPException(404, detail="StorageType not found")

    update_data = storage_type_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(storage_type, k, v)

    await session.commit()


@storage_type_router.delete(
    "/storagetype/{id}",
    summary="Delete a StorageType",
    status_code=204,
)
async def delete_storage_type(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(
        select(models.StorageType).where(models.StorageType.id == id)
    )
    storage_type = result.first()
    if storage_type is None:
        raise HTTPException(404, detail="StorageType not found")

    await session.delete(storage_type)
    await session.commit()
