from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    comment: str = Field(description="The comment")


class CommentCreate(CommentBase):
    item_id: int = Field(description="The Item ID to map the comment to")

    class Config:
        json_schema_extra = {
            "example": {
                "comment": "The item has just been put into storage!",
                "item_id": 54,
            }
        }


class CommentRead(CommentBase, TimestampSchema):
    id: int = Field()
    item_id: int = Field()
    user_id: int | None = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 76,
                "comment": "The item has just been put into storage!",
                "user_id": 3,
                "item_id": 54,
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
