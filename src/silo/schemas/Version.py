from pydantic import BaseModel, Field

from silo import config


class Version(BaseModel):
    current: str = Field(default=config.api_version)
    available: list[str] = Field()
    endpoints: dict[str, list | str] = Field()

    class Config:
        json_schema_extra = {
            "example": {
                "current": "v1",
                "available": ["v1"],
                "endpoints": {
                    "current": "/api/",
                    "v1": "/api/v1/",
                },
            }
        }
