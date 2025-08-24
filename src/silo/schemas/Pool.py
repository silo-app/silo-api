from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class PoolBase(BaseModel):

    name: str = Field()
    description: str = Field()


class PoolCreate(PoolBase):

    class Config:
        json_schema_extra = {
            "example": {
                "name": "inv",
                "description": "Inventary",
            }
        }


class PoolRead(PoolBase, TimestampSchema):

    id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "id": 3,
                "name": "inv",
                "description": "Inventary",
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
