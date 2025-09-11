from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from silo.database.models import Base
from silo.database.models.Base import TimestampMixin


class Comment(Base, TimestampMixin):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    comment: Mapped[str] = mapped_column("name", nullable=False)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), nullable=False)
    user_id: Mapped[int] | None = mapped_column(
        ForeignKey("user.id"), nullable=True, default_factory=None
    )
