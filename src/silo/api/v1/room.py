from fastapi import Depends, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import RoomBase, RoomCreate, RoomRead

room_router = APIRouter(tags=["Room"], dependencies=[Depends(require_permission())])


@room_router.get(
    "/room/",
    summary="Get all Rooms",
    response_model=list[RoomRead],
)
@room_router.get(
    "/room/{id}",
    summary="Get a specific Room",
    response_model=RoomRead,
)
async def get_rooms(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> RoomRead | list[RoomRead]:
    if id is not None:
        result = await session.scalars(select(models.Room).where(models.Room.id == id))
        room = result.one_or_none()

        if room is not None:
            return RoomRead.model_validate(room, from_attributes=True)

        raise HTTPException(status_code=404, detail=f"Room {id} not found")

    result = await session.scalars(select(models.Room))
    rooms = result.all()

    return [RoomRead.model_validate(room, from_attributes=True) for room in rooms]


@room_router.post(
    "/room/",
    summary="Add a new Room",
    response_model=RoomRead,
    status_code=201,
)
async def new_room(
    room: RoomCreate, session: AsyncSession = Depends(async_get_db)
) -> RoomRead:
    new_room = models.Room(**room.model_dump())
    session.add(new_room)
    await session.commit()
    return new_room


@room_router.put(
    "/room/{id}",
    summary="Update an existing Room",
    status_code=204,
)
async def update_room(
    id: int, room_update: RoomCreate, session: AsyncSession = Depends(async_get_db)
):
    result = await session.scalars(select(models.Room).where(models.Room.id == id))
    room = result.one_or_none()
    if room is None:
        raise HTTPException(404, detail="Room not found")

    update_data = room_update.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        setattr(room, k, v)

    await session.commit()


@room_router.delete(
    "/room/{id}",
    summary="Delete a Room",
    status_code=204,
)
async def delete_room(id: int, session: AsyncSession = Depends(async_get_db)):
    result = await session.scalars(select(models.Room).where(models.Room.id == id))
    room = result.one_or_none()
    if room is None:
        raise HTTPException(404, detail="Room not found")

    await session.delete(room)
    await session.commit()
