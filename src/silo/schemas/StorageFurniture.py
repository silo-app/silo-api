from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class StorageFurnitureBase(BaseModel):
    name: str = Field()
    room_id: int = Field()
    storage_type_id: int = Field()


class StorageFurnitureCreate(StorageFurnitureBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "C-1",
                "room_id": 2,
                "storage_type_id": 1,
            }
        }


class StorageFurnitureRead(StorageFurnitureBase, TimestampSchema):
    id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "id": 35,
                "storage_type": 3,
                "created_at": "2025-07-18T13:15:57.123232",
                "updated_at": "2025-08-11T09:24:11.123232",
            }
        }
