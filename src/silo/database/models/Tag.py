from typing import TYPE_CHECKING
from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship

from silo.database.models.ItemTag import item_tag_association

if TYPE_CHECKING:
    from silo.database.models import Item


class Tag(Base, TimestampMixin):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    name: Mapped[str] = mapped_column("name", nullable=False, unique=True)
    color_hex: Mapped[str] = mapped_column("color_hex", nullable=False)
    text_dark: Mapped[bool]

    items: Mapped[list["Item"]] = relationship(
        "Item",
        secondary=item_tag_association,
        back_populates="tags",
    )
