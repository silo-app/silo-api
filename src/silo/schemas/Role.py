from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class RoleBase(BaseModel):

    name: str = Field(min_length=2, max_length=100)
    permissions: dict[str, list[str]]


class RoleCreate(RoleBase):

    class Config:
        json_schema_extra = {
            "example": {
                "name": "user",
                "permissions": {
                    "/item/*": ["GET"],
                    "/role/*": ["GET"],
                    "/pool/*": ["GET", "POST"],
                },
            }
        }


class RoleRead(RoleBase, TimestampSchema):

    id: int = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "id": 2,
                "name": "user",
                "permissions": {
                    "/item/*": ["GET"],
                    "/role/*": ["GET"],
                    "/,pool/*": ["GET", "POST"],
                },
            }
        }
