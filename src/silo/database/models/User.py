from sqlalchemy import Boolean, Integer, String
from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from silo.database.models.UserRole import user_roles_association

if TYPE_CHECKING:
    from silo.database.models import Role


class User(Base, TimestampMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )

    username: Mapped[str] = mapped_column(String(15), unique=True, index=True)

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles_association,
        back_populates="users",
        init=False,
        default_factory=list,
        lazy="selectin",
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
