from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from silo.database import async_get_db
from silo.database import models
from silo.api.v1 import ErrorResponse
from silo.schemas import (
    StorageFurnitureBase,
    StorageFurnitureCreate,
    StorageFurnitureRead,
)

storage_furniture_router = APIRouter(tags=["StorageFurniture"])


@storage_furniture_router.get(
    "/storagefurniture/",
    summary="Get all StorageFurnitures",
    response_model=list[StorageFurnitureRead],
)
@storage_furniture_router.get(
    "/storagefurniture/{id}",
    summary="Get a specific StorageFurniture",
    response_model=StorageFurnitureRead,
)
async def get_storage_furnitures(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> StorageFurnitureRead | list[StorageFurnitureRead]:
    if id is not None:
        result = await session.scalars(
            select(models.StorageFurniture).where(models.StorageFurniture.id == id)
        )
        storage_furniture = result.one_or_none()

        if storage_furniture is not None:
            return StorageFurnitureRead.model_validate(storage_furniture)

        raise HTTPException(status_code=404, detail=f"StorageFurniture {id} not found")

    result = await session.scalars(select(models.StorageFurniture))
    storage_furnitures = result.all()

    return [
        StorageFurnitureRead.model_validate(storage_furniture, from_attributes=True)
        for storage_furniture in storage_furnitures
    ]


@storage_furniture_router.post(
    "/storagefurniture/",
    summary="Add a new StorageFurniture",
    response_model=StorageFurnitureRead,
    status_code=201,
    responses={
        409: {"model": ErrorResponse, "description": "Unique constraint violation"}
    },
)
async def new_storage_furniture(
    storage_furniture: StorageFurnitureCreate,
    session: AsyncSession = Depends(async_get_db),
) -> StorageFurnitureRead:
    new_storage_furniture = models.StorageFurniture(**storage_furniture.model_dump())
    try:
        session.add(new_storage_furniture)
        await session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="This combination of name, room and type might already exists!",
        )

    return new_storage_furniture


@storage_furniture_router.put(
    "/storagefurniture/{id}",
    summary="Update an existing StorageFurniture",
    status_code=204,
)
async def update_storage_furniture(
    id: int,
    storage_furniture_update: StorageFurnitureCreate,
    session: AsyncSession = Depends(async_get_db),
):
    result = await session.scalars(
        select(models.StorageFurniture).where(models.StorageFurniture.id == id)
    )
    storage_furniture = result.first()
    if storage_furniture is None:
        raise HTTPException(404, detail="StorageFurniture not found")

    update_data = storage_furniture_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(storage_furniture, k, v)

    await session.commit()


@storage_furniture_router.delete(
    "/storagefurniture/{id}",
    summary="Delete a StorageFurniture",
    status_code=204,
)
async def delete_storage_furniture(
    id: int, session: AsyncSession = Depends(async_get_db)
):
    result = await session.scalars(
        select(models.StorageFurniture).where(models.StorageFurniture.id == id)
    )
    storage_furniture = result.first()
    if storage_furniture is None:
        raise HTTPException(404, detail="StorageFurniture not found")

    await session.delete(storage_furniture)
    await session.commit()
