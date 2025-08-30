from typing import TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from silo.database.models import Base
from silo.database.models.Base import TimestampMixin

if TYPE_CHECKING:
    from silo.database.models import StorageArea


class Item(Base, TimestampMixin):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    silo_id: Mapped[str] = mapped_column(unique=True, index=True)

    type_id: Mapped[int] = mapped_column(ForeignKey("item_type.id"))
    pool_id: Mapped[int] = mapped_column(ForeignKey("pool.id"))

    name: Mapped[str]
    description: Mapped[str]
    quantity: Mapped[int]

    sequence_num: Mapped[int] = mapped_column()

    storage_area_id: Mapped[int] = mapped_column(
        ForeignKey("storage_area.id"), nullable=False
    )
    storage_area: Mapped["StorageArea"] = relationship(
        back_populates="items", lazy="selectin", init=False
    )

    weight: Mapped[int | None] = mapped_column(default=None)
    serial_number: Mapped[str | None] = mapped_column(default=None)
    deleted: Mapped[bool] = mapped_column(default=False)
    inventory_number: Mapped[str | None] = mapped_column(default=None)

    __table_args__ = (
        UniqueConstraint("type_id", "pool_id", "sequence_num", name="silo_item_id"),
    )
