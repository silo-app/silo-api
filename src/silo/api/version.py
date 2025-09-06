from fastapi import APIRouter

from silo import config
from silo.schemas import Version

version_router = APIRouter(tags=["version"])


@version_router.get(
    "/version",
    response_description="Get available API versions and the current app version",
    status_code=200,
    response_model=Version,
    summary="Get all API versions and the current app version",
)
async def version():
    return {
        "app_version": config.version,
        "current": config.api_version,
        "available": ["v1"],
        "endpoints": {
            "current": config.api_version,
            "v1": "/api/v1/",
        },
    }
