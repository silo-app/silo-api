from __future__ import annotations
from typing import TYPE_CHECKING

from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field

from .StorageArea import StorageAreaRead

if TYPE_CHECKING:
    from silo.schemas import TagRead


class ItemBase(BaseModel):
    name: str = Field()
    description: str = Field()
    quantity: int = Field()

    weight: int | None = Field(default=None)
    serial_number: str | None = Field(default=None)
    inventory_number: str | None = Field(default=None)
    deleted: bool = Field(default=False)


class ItemCreate(ItemBase):
    type_id: int = Field()
    pool_id: int = Field()
    storage_area_id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "type_id": 2,
                "pool_id": 4,
                "storage_area_id": 32,
                "name": "3m Ethernet cable CAT.8",
                "description": "3m yellow ethernet cable (CAT.8)",
                "quantity": 3,
                "weight": 320,
                "serial_number": "1200958493",
                "inventory_number": "4001-2384-88572",
                "deleted": False,
            }
        }


class ItemRead(ItemBase, TimestampSchema):
    id: int = Field()
    silo_id: str = Field()
    storage_area: StorageAreaRead
    tags: list["TagRead"] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 12,
                "name": "3m Ethernet cable CAT.8",
                "description": "3m yellow ethernet cable (CAT.8)",
                "quantity": 3,
                "weight": 320,
                "serial_number": "1200958493",
                "inventory_number": "4001-2384-88572",
                "deleted": False,
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
