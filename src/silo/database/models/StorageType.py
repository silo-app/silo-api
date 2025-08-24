from sqlalchemy import ForeignKey
from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship


class StorageType(Base, TimestampMixin):
    __tablename__ = "storage_type"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    name: Mapped[str] = mapped_column("name", nullable=False, unique=True)
