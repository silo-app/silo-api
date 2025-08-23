from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column

class ItemType(Base, TimestampMixin):
    __tablename__ = "item_type"

    id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    name: Mapped[str]
    description: Mapped[str]

