from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import get_current_user, require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import CommentCreate, CommentRead
from silo.schemas.User import UserRead

comment_router = APIRouter(
    tags=["Comment"], dependencies=[Depends(require_permission())]
)


@comment_router.get(
    "/comment/",
    summary="Get all Comments",
    response_model=list[CommentRead],
)
@comment_router.get(
    "/comment/{id}",
    summary="Get a specific Comment",
    response_model=CommentRead,
)
async def get_comments(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> CommentRead | list[CommentRead]:
    if id is not None:
        result = await session.scalars(
            select(models.Comment).where(models.Comment.id == id)
        )
        comment = result.one_or_none()

        if comment is not None:
            return CommentRead.model_validate(comment, from_attributes=True)

        raise HTTPException(status_code=404, detail=f"Comment {id} not found")

    result = await session.scalars(select(models.Comment))
    comments = result.all()

    return [
        CommentRead.model_validate(comment, from_attributes=True)
        for comment in comments
    ]


@comment_router.post(
    "/comment/",
    summary="Add a new Comment",
    response_model=CommentRead,
    status_code=201,
)
async def new_comment(
    comment: CommentCreate,
    session: AsyncSession = Depends(async_get_db),
    user: UserRead = Depends(get_current_user),
) -> CommentRead:
    new_comment_data = comment.model_dump()
    new_comment_data["user_id"] = user.id
    new_comment = models.Comment(**new_comment_data)
    session.add(new_comment)
    await session.commit()
    await session.refresh(new_comment)
    return new_comment


@comment_router.put(
    "/comment/{id}",
    summary="Update an existing Comment",
    status_code=204,
)
async def update_comment(
    id: int,
    comment_update: CommentCreate,
    session: AsyncSession = Depends(async_get_db),
):
    result = await session.scalars(
        select(models.Comment).where(models.Comment.id == id)
    )
    comment = result.one_or_none()
    if comment is None:
        raise HTTPException(404, detail="Comment not found")

    update_data = comment_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(comment, k, v)

    await session.commit()


@comment_router.delete(
    "/comment/{id}",
    summary="Delete a Comment",
    status_code=204,
)
async def delete_comment(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(
        select(models.Comment).where(models.Comment.id == id)
    )
    comment = result.one_or_none()
    if comment is None:
        raise HTTPException(404, detail="Comment not found")

    await session.delete(comment)
    await session.commit()
