from fastapi import APIRouter

from silo import config
from silo.schemas import Version

version_router = APIRouter(tags=["version"])


@version_router.get(
    "/version",
    response_description="Get application version",
    status_code=200,
    response_model=Version,
    summary="Get app name, app version and stable API version",
)
async def version():
    return {
        "app_name": config.app_name,
        "version": config.version,
    }
