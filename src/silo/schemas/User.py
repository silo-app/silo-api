from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field

from silo.schemas.Role import RoleRead


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    is_active: bool = True


class UserBase(UserUpdate):
    username: str


class UserCreate(UserBase):
    class Config:
        json_schema_extra = {
            "example": {
                "username": "maxi",
                "full_name": "Max Mustermann",
                "email": "max.mustermann@example.com",
                "is_active": True,
            }
        }


class UserRead(UserBase, TimestampSchema):
    id: int = Field()
    roles: list[RoleRead] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 5,
                "username": "maxi",
                "full_name": "Max Mustermann",
                "email": "max.mustermann@example.com",
                "is_active": True,
                "roles": ["admin"],
            }
        }
