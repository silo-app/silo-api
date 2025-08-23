from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.database import async_get_db
from silo.database import models
from silo.schemas import Item, ItemCollection, NewItem, UpdateItem

items_router = APIRouter(tags=["Item"])

@items_router.get(
    "/item/",
    summary="Get all Items",
    response_model=ItemCollection,
)
@items_router.get(
    "/item/{id}",
    summary="Get a specific Item",
    response_model=Item,
)
async def get_items(session: AsyncSession = Depends(async_get_db), id: int | None = None) -> Item | list[Item]:
    if id is not None:
        item = await session.get(models.Item, int(id))

        if item is not None:
            return Item.model_validate(item)
        
        raise HTTPException(status_code=404, detail=f"Item {id} not found")
        
    items = await session.scalars(select(models.Item))
    list_all_items = items.all()
    if len(list_all_items) >= 1:
        all_items = []
        for item in list_all_items:
            item_dict = dict(item.__dict__)
            item_dict.pop('_sa_instance_state')
            all_items.append(item_dict)

        return JSONResponse(all_items, 200)
    else:
        return JSONResponse({}, 200)

@items_router.post(
    "/item/",
    summary="Add a new Item",
    response_model=Item,
    status_code=201,
)
async def new_item(item: NewItem, session: AsyncSession = Depends(async_get_db)) -> Item:
    print(item.model_dump())
    new_item = models.Item(**item.model_dump())
    session.add(new_item)
    await session.commit()
    return new_item

@items_router.put(
    "/item/{id}",
    summary="Update an existing Item",
    status_code=204,
)
async def update_item(id: int, update_data: UpdateItem, session: AsyncSession = Depends(async_get_db)):
    item = session.get(models.Item, int(id))
    if item is None:
        raise HTTPException(404, detail="Item not found")

    for k, v in vars(update_data).items():
        setattr(item, k, v)

    await session.commit()


@items_router.delete(
    "/item/{id}",
    summary="Delete an Item",
    status_code=204,
)
async def delete_item(id: int, session: AsyncSession = Depends(async_get_db)):

    item = session.get(models.Item, int(id))
    if item is None:
        raise HTTPException(404, detail="Item not found")

    await session.delete(item)
    await session.commit()
