from fastapi import APIRouter
from .version import version_router
from .auth import login_router, logout_router

from .item import items_router
from .room import room_router
from .pool import pool_router
from .itemtype import item_type_router

router = APIRouter(prefix="/v1")


router.include_router(login_router)
router.include_router(logout_router)

router.include_router(version_router)


router.include_router(items_router)
router.include_router(item_type_router)
router.include_router(room_router)
router.include_router(pool_router)
