from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from silo.database import async_get_db
from silo.database import models
from silo.schemas import Response, UserCreate, UserRead, UserUpdate
from silo.api.dependencies import get_current_user, require_permission

user_router = APIRouter(tags=["User"], dependencies=[Depends(require_permission())])


@user_router.get(
    "/user/",
    summary="Get all Users",
    response_model=list[UserRead],
)
@user_router.get(
    "/user/{id}",
    summary="Get a specific User",
    response_model=UserRead,
)
async def get_users(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> UserRead | list[UserRead]:
    if id is not None:
        result = await session.scalars(select(models.User).where(models.User.id == id))
        user = result.one_or_none()

        if user is not None:
            return UserRead.model_validate(user, from_attributes=True)

        raise HTTPException(status_code=404, detail=f"User {id} not found")

    result = await session.scalars(select(models.User).options(selectinload(models.User.roles)))
    users = result.all()

    return [UserRead.model_validate(user, from_attributes=True) for user in users]


@user_router.get("/myinfo", summary="Get my user information", response_model=UserRead)
async def get_me(
    user: UserRead = Depends(get_current_user),
):
    return user


@user_router.post(
    "/user/",
    summary="Add a new User",
    response_model=UserRead,
    status_code=201,
    responses={
        409: {"model": Response, "description": "Unique constraint violation"},
    },
)
async def new_user(user: UserCreate, session: AsyncSession = Depends(async_get_db)) -> UserRead:
    data = user.model_dump(exclude=("roles"))
    new_user = models.User(**data)
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        await session.refresh(new_user, attribute_names=["roles"])
    except IntegrityError:
        raise HTTPException(
            409,
            detail=f"The user with the username {new_user.username} already exists!",
        )

    return new_user


@user_router.post(
    "/user/{user_id}/roles/{role_id}",
    summary="Assign a Role to a User",
    responses={404: {"model": Response, "description": "Not found"}},
)
async def assign_role(
    user_id: int, role_id: int, session: AsyncSession = Depends(async_get_db)
) -> UserRead:
    result_u = await session.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user_id)
    )
    user: models.User | None = result_u.scalars().first()
    if user is None:
        raise HTTPException(404, detail="User not found")
    result_r = await session.scalars(select(models.Role).where(models.Role.id == role_id))
    role = result_r.one_or_none()
    if role is None:
        raise HTTPException(404, detail="Role not found")

    if role not in user.roles:
        user.roles.append(role)

    await session.commit()

    result = await session.execute(
        select(models.User)
        .options(selectinload(models.User.roles))
        .where(models.User.id == user_id)
    )
    user = result.scalar_one()

    return user


@user_router.put(
    "/user/{id}",
    summary="Update an existing User",
    status_code=204,
)
async def update_user(
    id: int, user_update: UserUpdate, session: AsyncSession = Depends(async_get_db)
):
    result = await session.scalars(select(models.User).where(models.User.id == id))
    user = result.one_or_none()
    if user is None:
        raise HTTPException(404, detail="User not found")

    update_data = user_update.model_dump()
    for k, v in update_data.items():
        setattr(user, k, v)

    await session.commit()
    await session.refresh(user)


@user_router.delete(
    "/user/{id}",
    summary="Delete a User",
    status_code=204,
)
async def delete_user(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.User).where(models.User.id == id))
    user = result.one_or_none()
    if user is None:
        raise HTTPException(404, detail="User not found")

    await session.delete(user)
    await session.commit()
