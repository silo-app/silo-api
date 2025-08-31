from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field

from silo.schemas.Role import RoleRead


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    class Config:
        json_schema_extra = {
            "example": {
                "username": "maxi",
            }
        }


class UserRead(UserBase, TimestampSchema):
    id: int = Field()
    roles: list[RoleRead] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {"id": 5, "username": "maxi", "roles": ["admin"]}
        }
