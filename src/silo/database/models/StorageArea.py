from typing import TYPE_CHECKING, Optional
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from silo.database.models import Base
from silo.database.models.Base import TimestampMixin

if TYPE_CHECKING:
    from silo.database.models import Room, StorageFurniture, Item


class StorageArea(Base, TimestampMixin):
    __tablename__ = "storage_area"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    area: Mapped[str] = mapped_column(String(100), nullable=False)

    room_id: Mapped[int] = mapped_column(
        ForeignKey("room.id"), nullable=False, init=False
    )
    furniture_id: Mapped[int] = mapped_column(
        ForeignKey("storage_furniture.id"), nullable=False, init=False
    )

    room: Mapped[Optional["Room"]] = relationship(
        back_populates="storage_areas", lazy="selectin", default=None
    )
    furniture: Mapped[Optional["StorageFurniture"]] = relationship(
        back_populates="storage_areas", lazy="selectin", default=None
    )

    items: Mapped[list["Item"]] = relationship(
        back_populates="storage_area", lazy="selectin", default_factory=list
    )

    __table_args__ = (
        UniqueConstraint("room_id", "furniture_id", "area", name="unique_storage_area"),
    )
