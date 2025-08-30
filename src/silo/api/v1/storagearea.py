from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import StorageAreaCreate, StorageAreaRead

storage_area_router = APIRouter(
    tags=["StorageArea"], dependencies=[Depends(require_permission())]
)


@storage_area_router.get(
    "/storagearea/",
    summary="Get all StorageAreas",
    response_model=list[StorageAreaRead],
)
@storage_area_router.get(
    "/storagearea/{id}",
    summary="Get a specific StorageArea",
    response_model=StorageAreaRead,
)
async def get_storage_areas(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> StorageAreaRead | list[StorageAreaRead]:
    if id is not None:
        result = await session.scalars(
            select(models.StorageArea).where(models.StorageArea.id == id)
        )
        storage_area = result.one_or_none()

        if storage_area is not None:
            return StorageAreaRead.model_validate(storage_area)

        raise HTTPException(status_code=404, detail=f"StorageArea {id} not found")

    result = await session.scalars(select(models.StorageArea))
    storage_areas = result.all()

    return [
        StorageAreaRead.model_validate(storage_area, from_attributes=True)
        for storage_area in storage_areas
    ]


@storage_area_router.post(
    "/storagearea/",
    summary="Add a new StorageArea",
    response_model=StorageAreaRead,
    status_code=201,
)
async def new_storage_area(
    storage_area: StorageAreaCreate, session: AsyncSession = Depends(async_get_db)
) -> StorageAreaRead:
    room = await session.get(models.Room, storage_area.room_id)
    furniture = await session.get(models.StorageFurniture, storage_area.furniture_id)

    new_storage_area = models.StorageArea(
        area=storage_area.area,
        room=room,
        furniture=furniture,
    )
    session.add(new_storage_area)
    await session.commit()
    await session.refresh(new_storage_area)
    return new_storage_area


@storage_area_router.put(
    "/storagearea/{id}",
    summary="Update an existing StorageArea",
    status_code=204,
)
async def update_storage_area(
    id: int,
    storage_area_update: StorageAreaCreate,
    session: AsyncSession = Depends(async_get_db),
):
    result = await session.scalars(
        select(models.StorageArea).where(models.StorageArea.id == id)
    )
    storage_area = result.first()
    if storage_area is None:
        raise HTTPException(404, detail="StorageArea not found")

    update_data = storage_area_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(storage_area, k, v)

    await session.commit()


@storage_area_router.delete(
    "/storagearea/{id}",
    summary="Delete a StorageArea",
    status_code=204,
)
async def delete_storage_area(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(
        select(models.StorageArea).where(models.StorageArea.id == id)
    )
    storage_area = result.first()
    if storage_area is None:
        raise HTTPException(404, detail="StorageArea not found")

    await session.delete(storage_area)
    await session.commit()
