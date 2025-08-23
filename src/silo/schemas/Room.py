from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class RoomBase(BaseModel):

    
    name: str = Field()
    description: str = Field()
    

class RoomCreate(RoomBase):

    class Config:
        json_schema_extra = {
            "example": {
                "name": "F0.412",
                "description": "Storage room",
            }
        }


class RoomRead(RoomBase, TimestampSchema):

    id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "id": 7,
                "name": "F0.412",
                "description": "Storage room",
                "created_at": "2025-08-23T06:03:59.939083Z",
                "updated_at": "2025-08-24T12:03:59.939083Z",
            }
        }
