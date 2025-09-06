from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, or_, and_

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import ItemCreate, ItemRead, ItemSearch

items_router = APIRouter(tags=["Item"], dependencies=[Depends(require_permission())])


@items_router.get(
    "/item/search",
    summary="Search Items",
    response_model=list[ItemRead],
)
async def search_items(
    params: ItemSearch = Depends(),
    session: AsyncSession = Depends(async_get_db),
):
    search_conditions = []
    statement = select(models.Item)

    if params.q:
        search_conditions.append(
            or_(
                models.Item.name.ilike(f"%{params.q}%"),
                models.Item.description.ilike(f"%{params.q}%"),
            )
        )

    if params.room_id:
        statement = statement.join(models.Item.storage_area)
        search_conditions.append(models.StorageArea.room_id == params.room_id)

    if params.furniture_id:
        if not params.room_id:
            statement = statement.join(models.Item.storage_area)
        search_conditions.append(models.StorageArea.furniture_id == params.furniture_id)

    if search_conditions:
        statement = statement.where(and_(*search_conditions))

    # pagination
    statement = statement.limit(params.limit).offset(params.offset)

    result = await session.scalars(statement)
    return result.all()


@items_router.get(
    "/item/",
    summary="Get all Items",
    response_model=list[ItemRead],
)
@items_router.get(
    "/item/{id}",
    summary="Get a specific Item",
    response_model=ItemRead,
    responses={403: {"description": "Forbidden – missing required permissions"}},
)
async def get_items(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> ItemRead | list[ItemRead]:
    if id is not None:
        result = await session.scalars(select(models.Item).where(models.Item.id == id))
        item = result.one_or_none()

        if item is not None:
            return ItemRead.model_validate(item)

        raise HTTPException(status_code=404, detail=f"Item {id} not found")

    result = await session.scalars(select(models.Item))
    items = result.all()

    return [ItemRead.model_validate(item, from_attributes=True) for item in items]


@items_router.get(
    "/item/by-silo-id/{silo_id}",
    summary="Get a specific Item using the SILO id",
    response_model=ItemRead,
    responses={403: {"description": "Forbidden – missing required permissions"}},
)
async def get_item_by_silo_id(
    silo_id: str,
    session: AsyncSession = Depends(async_get_db),
):
    if silo_id is not None:
        result = await session.scalars(
            select(models.Item).where(models.Item.silo_id == silo_id)
        )
        item = result.one_or_none()
        if item is not None:
            return ItemRead.model_validate(item)

    raise HTTPException(
        status_code=404, datail=f"Item with SILO id {silo_id} not found!"
    )


@items_router.post(
    "/item/{item_id}/tags/{tag_id}",
    summary="Assign a Tag to an Item",
    response_model=ItemRead,
)
async def assign_tag(
    item_id: int, tag_id: int, session: AsyncSession = Depends(async_get_db)
) -> ItemRead:
    item: ItemRead = session.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    tag = session.get(models.Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

    if tag not in item.tags:
        item.tags.append(tag)
        await session.commit()
        await session.refresh(item)

    return item


@items_router.delete(
    "/item/{item_id}/tags/{tag_id}",
    summary="Delete a Tag on an Item",
    response_model=ItemRead,
)
async def delete_assigned_tag(
    item_id: int, tag_id: int, session: AsyncSession = Depends(async_get_db)
) -> ItemRead:
    item: ItemRead = session.get(models.Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    tag = session.get(models.Tag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail=f"Tag {tag_id} not found")

    if tag in item.tags:
        item.tags.remove(tag)
        await session.commit()
        await session.refresh(item)

    return item


@items_router.post(
    "/item/",
    summary="Add a new Item",
    response_model=ItemRead,
    status_code=201,
)
async def new_item(
    item: ItemCreate, session: AsyncSession = Depends(async_get_db)
) -> ItemRead:
    # no need to check if None, pydantic does validation
    type_id = item.type_id
    pool_id = item.pool_id

    result = await session.scalars(
        select(
            func.max(models.Item.sequence_num).filter(
                models.Item.type_id == type_id, models.Item.pool_id == pool_id
            )
        )
    )
    sequence_num = result.first()

    next_sequence_num = (sequence_num or 0) + 1

    result_type_name = await session.scalars(
        select(models.ItemType.name).where(models.ItemType.id == type_id)
    )
    type_name = result_type_name.one_or_none()
    result_pool_name = await session.scalars(
        select(models.Pool.name).where(models.Pool.id == pool_id)
    )
    pool_name = result_pool_name.one_or_none()

    silo_id = f"{type_name}-{pool_name}-{next_sequence_num:04d}"

    new_item = models.Item(
        **item.model_dump(), sequence_num=next_sequence_num, silo_id=silo_id
    )
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)
    return new_item


@items_router.put(
    "/item/{id}",
    summary="Update an existing Item",
    status_code=204,
)
async def update_item(
    id: int, item_update: ItemCreate, session: AsyncSession = Depends(async_get_db)
):
    result = await session.scalars(select(models.Item).where(models.Item.id == id))
    item = result.first()
    if item is None:
        raise HTTPException(404, detail="Item not found")

    update_data = item_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(item, k, v)

    await session.commit()
    await session.refresh(item)


@items_router.patch(
    "/item-delete/{id}",
    summary="Mark an Item as deleted",
    status_code=204,
)
async def mark_item_as_deleted(id: int, session: AsyncSession = Depends(async_get_db)):
    item: ItemRead = session.get(models.Item, id)

    if item is None:
        raise HTTPException(404, detail="Item not found")

    item.deleted = True

    await session.commit()
    await session.refresh(item)


@items_router.delete(
    "/item/{id}",
    summary="Delete an Item from database",
    status_code=204,
)
async def delete_item(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.Item).where(models.Item.id == id))
    item = result.first()
    if item is None:
        raise HTTPException(404, detail="Item not found")

    await session.delete(item)
    await session.commit()
