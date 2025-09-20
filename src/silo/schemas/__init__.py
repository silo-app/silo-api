from . import Base
from .Token import Token
from .Version import Version
from .Response import Response
from .AuthData import AuthData, UserAttributes

from .Item import ItemBase, ItemCreate, ItemRead
from .ItemType import ItemTypeBase, ItemTypeCreate, ItemTypeRead
from .ItemSearch import ItemSearch
from .Room import RoomBase, RoomCreate, RoomRead
from .Pool import PoolBase, PoolCreate, PoolRead
from .User import UserBase, UserCreate, UserRead, UserUpdate
from .Role import RoleBase, RoleCreate, RoleRead
from .StorageType import StorageTypeBase, StorageTypeCreate, StorageTypeRead
from .StorageArea import StorageAreaBase, StorageAreaCreate, StorageAreaRead
from .StorageFurniture import (
    StorageFurnitureBase,
    StorageFurnitureCreate,
    StorageFurnitureRead,
)
from .Tag import TagBase, TagRead, TagCreate
from .Comment import CommentBase, CommentRead, CommentCreate

from .BatteryType import BatteryType
from .Document import (
    DocumentRead,
    DocumentCreate,
    DocumentUpdate,
    DocumentMimeTypes,
    DocumentType,
)

ItemRead.model_rebuild()
TagRead.model_rebuild()
