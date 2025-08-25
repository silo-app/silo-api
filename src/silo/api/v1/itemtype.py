from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import ItemTypeBase, ItemTypeCreate, ItemTypeRead

item_type_router = APIRouter(
    tags=["ItemType"], dependencies=[Depends(require_permission())]
)


@item_type_router.get(
    "/itemtype/",
    summary="Get all ItemTypes",
    response_model=list[ItemTypeRead],
)
@item_type_router.get(
    "/itemtype/{id}",
    summary="Get a specific ItemType",
    response_model=ItemTypeRead,
)
async def get_item_types(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> ItemTypeRead | list[ItemTypeRead]:
    if id is not None:
        result = await session.scalars(
            select(models.ItemType).where(models.ItemType.id == id)
        )
        item_type = result.one_or_none()

        if item_type is not None:
            return ItemTypeRead.model_validate(item_type)

        raise HTTPException(status_code=404, detail=f"ItemType {id} not found")

    result = await session.scalars(select(models.ItemType))
    item_types = result.all()

    return [
        ItemTypeRead.model_validate(item_type, from_attributes=True)
        for item_type in item_types
    ]


@item_type_router.post(
    "/itemtype/",
    summary="Add a new ItemType",
    response_model=ItemTypeRead,
    status_code=201,
)
async def new_item_type(
    item_type: ItemTypeCreate, session: AsyncSession = Depends(async_get_db)
) -> ItemTypeRead:
    new_item_type = models.ItemType(**item_type.model_dump())
    session.add(new_item_type)
    await session.commit()
    return new_item_type


@item_type_router.put(
    "/itemtype/{id}",
    summary="Update an existing ItemType",
    status_code=204,
)
async def update_item_type(
    id: int,
    item_type_update: ItemTypeCreate,
    session: AsyncSession = Depends(async_get_db),
):
    result = await session.scalars(
        select(models.ItemType).where(models.ItemType.id == id)
    )
    item_type = result.first()
    if item_type is None:
        raise HTTPException(404, detail="ItemType not found")

    update_data = item_type_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(item_type, k, v)

    await session.commit()


@item_type_router.delete(
    "/itemtype/{id}",
    summary="Delete an ItemType",
    status_code=204,
)
async def delete_item_type(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(
        select(models.ItemType).where(models.ItemType.id == id)
    )
    item_type = result.first()
    if item_type is None:
        raise HTTPException(404, detail="ItemType not found")

    await session.delete(item_type)
    await session.commit()
