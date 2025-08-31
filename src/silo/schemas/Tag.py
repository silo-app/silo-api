from typing import TYPE_CHECKING
from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from silo.schemas import ItemRead


class TagBase(BaseModel):
    name: str = Field()
    color_hex: str = Field()
    text_dark: bool = Field(default=False)


class TagCreate(TagBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "cable",
                "color_hex": "#fbff00",
                "text_dark": True,
            }
        }


class TagRead(TagBase, TimestampSchema):
    id: int = Field()
    item: list["ItemRead"] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "cable",
                "color_hex": "#1c5d96",
                "text_dark": False,
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
