from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class ItemTypeBase(BaseModel):

    name: str = Field()
    description: str = Field()


class ItemTypeCreate(ItemTypeBase):

    class Config:
        json_schema_extra = {
            "example": {
                "name": "stock",
                "description": "Warehouse stock",
            }
        }


class ItemTypeRead(ItemTypeBase, TimestampSchema):

    id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "id": 7,
                "name": "stock",
                "description": "Warehouse stock",
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
