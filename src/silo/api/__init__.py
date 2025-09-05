from .v1 import router as v1_router
from fastapi import APIRouter

from silo import config


router = APIRouter()

AVAILABLE_VERSIONS = {
    "v1": v1_router,
}

try:
    # latest API version (set by the configuration file)
    router.include_router(AVAILABLE_VERSIONS[config.api_version], prefix="/api")
except KeyError:
    raise RuntimeError(
        f"Cannot create default API router. Please check if the specified version '{config.api_version}' exists!"
    )

# All API versions
router.include_router(v1_router, prefix="/api/v1", include_in_schema=False)
