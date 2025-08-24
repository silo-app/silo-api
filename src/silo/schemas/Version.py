from typing import Annotated
from pydantic import BaseModel, Field

from silo import config


class Version(BaseModel):

    app_name: Annotated[str, Field(default=config.app_name)]
    app_version: Annotated[str, Field(default=config.version)]
    api_version: Annotated[str, Field(default=config.api_version)]

    class Config:
        json_schema_extra = {
            "example": {
                "app_name": "SILO",
                "app_version": "1.0",
                "api_version": "v1",
            }
        }
