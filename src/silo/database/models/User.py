from datetime import datetime
from sqlalchemy import orm, DateTime
from datetime import UTC

from silo.database.models import Base


class User(Base):
    __tablename__ = "user"

    id: orm.Mapped[int] = orm.mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    username = orm.Mapped[str]
    email = orm.Mapped[str]
    full_name = orm.Mapped[str]
    is_active = orm.Mapped[bool]
    created_at: orm.Mapped[datetime] = orm.mapped_column(
        DateTime(timezone=True), default_factory=lambda: datetime.now(UTC)
    )
    updated_at: orm.Mapped[datetime | None] = orm.mapped_column(
        DateTime(timezone=True), default=None
    )
