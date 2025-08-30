from typing import Optional
from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field

from .Room import RoomRead
from .StorageFurniture import StorageFurnitureRead


class StorageAreaBase(BaseModel):
    area: str = Field()


class StorageAreaCreate(StorageAreaBase):
    room_id: int = Field()
    furniture_id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "area": "C1",
                "room_id": 4,
                "furniture_id": 2,
            }
        }


class StorageAreaRead(StorageAreaBase, TimestampSchema):
    id: int = Field()
    room: Optional[RoomRead]
    furniture: Optional[StorageFurnitureRead]

    class Config:
        json_schema_extra = {
            "example": {
                "created_at": "2025-08-30T10:09:11.958115Z",
                "updated_at": None,
                "area": "C",
                "id": 3,
                "room": {
                    "created_at": "2025-08-30T09:48:51.728726Z",
                    "updated_at": None,
                    "name": "D4.322",
                    "description": "Warehouse",
                    "id": 1,
                },
                "furniture": {
                    "created_at": "2025-08-30T09:49:23.685768Z",
                    "updated_at": None,
                    "name": "S-1",
                    "room_id": 1,
                    "storage_type_id": 1,
                    "id": 1,
                },
            }
        }
