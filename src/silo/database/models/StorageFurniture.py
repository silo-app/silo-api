from sqlalchemy import ForeignKey, UniqueConstraint
from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column


class StorageFurniture(Base, TimestampMixin):
    __tablename__ = "storage_furniture"

    # id: Mapped[int] = mapped_column("id", autoincrement=True, primary_key=True)
    # id: Mapped[int] = mapped_column("id", autoincrement=True, nullable=False, unique=True, primary_key=True, init=False)
    # id: Mapped[int] = mapped_column(Integer, Identity(), primary_key=True)
    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    name: Mapped[str] = mapped_column("name", nullable=False)

    room_id: Mapped[int] = mapped_column(ForeignKey("room.id"), nullable=False)
    storage_type_id: Mapped[int] = mapped_column(
        ForeignKey("storage_type.id"), nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "name", "room_id", "storage_type_id", name="unique_storage_furniture"
        ),
    )
