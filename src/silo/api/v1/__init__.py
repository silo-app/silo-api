from fastapi import APIRouter
from .version import version_router
from .auth import auth_router

from .user import user_router

from .item import items_router
from .room import room_router
from .pool import pool_router
from .itemtype import item_type_router
from .storagetype import storage_type_router
from .storagefurniture import storage_furniture_router
from .role import role_router

router = APIRouter(prefix="/v1")

router.include_router(version_router)

router.include_router(auth_router)

router.include_router(user_router)
router.include_router(role_router)


router.include_router(items_router)
router.include_router(item_type_router)
router.include_router(storage_type_router)
router.include_router(storage_furniture_router)
router.include_router(room_router)
router.include_router(pool_router)
