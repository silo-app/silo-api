from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from silo.database.models.UserRole import user_roles_association


class Role(Base, TimestampMixin):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    name: Mapped[str] = mapped_column("name", nullable=False, unique=True)
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles_association,
        back_populates="roles",
        default_factory=list,
        lazy="selectin",
    )
    permissions: Mapped[dict] = mapped_column(JSONB, default=dict)
