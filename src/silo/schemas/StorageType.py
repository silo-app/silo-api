from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class StorageTypeBase(BaseModel):
    name: str = Field()


class StorageTypeCreate(StorageTypeBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Cupboard",
            }
        }


class StorageTypeRead(StorageTypeBase, TimestampSchema):
    id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "id": 2,
                "name": "Cupboard",
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
