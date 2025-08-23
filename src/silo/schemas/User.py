from typing import Annotated
from silo.schemas import BaseSchemaAll
from pydantic import EmailStr, Field


class User(BaseSchemaAll):

    username: Annotated[str, Field(min_length=2, max_length=20, pattern=r"^[a-z0-9]+$", examples=["maxuser"])]
    email: Annotated[EmailStr, Field(examples=["user.userlast@example.com"])]
    full_name: Annotated[str, Field(examples=["Max Mustermann", "Maria Musterfrau"])]

    class Config:
        json_schema_extra = {
            "example": {
                "uuid": "XXXXXXXXXXXXX",
                "username": "maxmu",
                "email": "max.mustermann@silo-dev.de",
                "full_name": "Max Mustermann",
            }
        }