from silo.database.models import Base
from sqlalchemy.orm import Mapped, mapped_column


class StorageArea(Base):
    __tablename__ = "storage_area"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    name: Mapped[str]
    description: Mapped[str]
