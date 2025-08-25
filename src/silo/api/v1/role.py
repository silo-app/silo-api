from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import Response, RoleBase, RoleCreate, RoleRead

role_router = APIRouter(tags=["Role"], dependencies=[Depends(require_permission())])


@role_router.get(
    "/role/",
    summary="Get all Roles",
    response_model=list[RoleRead],
)
@role_router.get(
    "/role/{id}",
    summary="Get a specific Role",
    response_model=RoleRead,
)
async def get_roles(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> RoleRead | list[RoleRead]:
    if id is not None:
        result = await session.scalars(select(models.Role).where(models.Role.id == id))
        role = result.one_or_none()

        if role is not None:
            return RoleRead.model_validate(role, from_attributes=True)

        raise HTTPException(status_code=404, detail=f"Pool {id} not found")

    result = await session.scalars(select(models.Role))
    roles = result.all()

    return [RoleRead.model_validate(role, from_attributes=True) for role in roles]


@role_router.post(
    "/role/",
    summary="Add a new Role",
    response_model=RoleRead,
    status_code=201,
    responses={
        409: {"model": Response, "description": "Unique constraint violation"},
    },
)
async def new_role(
    role: RoleCreate, session: AsyncSession = Depends(async_get_db)
) -> RoleRead:
    new_role = models.Role(**role.model_dump())

    try:
        session.add(new_role)
        await session.commit()
        await session.refresh(new_role)
    except IntegrityError:
        raise HTTPException(
            409, f"A Role with the name {new_role.name} already exists!"
        )

    return new_role


@role_router.put(
    "/role/{id}",
    summary="Update an existing Role",
    status_code=204,
)
async def update_pool(
    id: int, role_update: RoleCreate, session: AsyncSession = Depends(async_get_db)
):
    result = await session.scalars(select(models.Role).where(models.Role.id == id))
    role = result.one_or_none()
    if role is None:
        raise HTTPException(404, detail="Role not found")

    update_data = role_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(role, k, v)

    await session.commit()


@role_router.delete(
    "/role/{id}",
    summary="Delete a Role",
    status_code=204,
)
async def delete_pool(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.Role).where(models.Role.id == id))
    role = result.one_or_none()
    if role is None:
        raise HTTPException(404, detail="Role not found")

    await session.delete(role)
    await session.commit()
