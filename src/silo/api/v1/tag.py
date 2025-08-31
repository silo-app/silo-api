from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import TagCreate, TagRead

tag_router = APIRouter(tags=["Tag"], dependencies=[Depends(require_permission())])


@tag_router.get(
    "/tag/",
    summary="Get all Tags",
    response_model=list[TagRead],
)
@tag_router.get(
    "/tag/{id}",
    summary="Get a specific Tag",
    response_model=TagRead,
)
async def get_tags(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> TagRead | list[TagRead]:
    if id is not None:
        result = await session.scalars(select(models.Tag).where(models.Tag.id == id))
        tag = result.one_or_none()

        if tag is not None:
            return TagRead.model_validate(tag, from_attributes=True)

        raise HTTPException(status_code=404, detail=f"Tag {id} not found")

    result = await session.scalars(select(models.Tag))
    tags = result.all()

    return [TagRead.model_validate(tag, from_attributes=True) for tag in tags]


@tag_router.post(
    "/tag/",
    summary="Add a new Tag",
    response_model=TagRead,
    status_code=201,
)
async def new_tag(
    tag: TagCreate, session: AsyncSession = Depends(async_get_db)
) -> TagRead:
    new_tag = models.Tag(**tag.model_dump())
    session.add(new_tag)
    await session.commit()
    return new_tag


@tag_router.put(
    "/tag/{id}",
    summary="Update an existing Tag",
    status_code=204,
)
async def update_tag(
    id: int, tag_update: TagCreate, session: AsyncSession = Depends(async_get_db)
):
    result = await session.scalars(select(models.Tag).where(models.Tag.id == id))
    tag = result.one_or_none()
    if tag is None:
        raise HTTPException(404, detail="Tag not found")

    update_data = tag_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(tag, k, v)

    await session.commit()


@tag_router.delete(
    "/tag/{id}",
    summary="Delete a Tag",
    status_code=204,
)
async def delete_tag(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.Tag).where(models.Tag.id == id))
    tag = result.one_or_none()
    if tag is None:
        raise HTTPException(404, detail="Tag not found")

    await session.delete(tag)
    await session.commit()
