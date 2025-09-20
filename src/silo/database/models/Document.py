from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM

from silo.database.models import Base
from silo.database.models.Base import TimestampMixin
from silo.schemas.Document import DocumentType, DocumentMimeTypes

DocumentMimeTypesEnum = ENUM(
    DocumentMimeTypes, name="mime_type_enum", create_type=True, metadata=Base.metadata
)


class Document(Base, TimestampMixin):
    __tablename__ = "document"

    id: Mapped[int] = mapped_column(
        "id",
        autoincrement=True,
        nullable=False,
        unique=True,
        primary_key=True,
        init=False,
    )
    filename: Mapped[str] = mapped_column()
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    file_size: Mapped[int] = mapped_column()
    mime_type: Mapped[DocumentMimeTypes] = mapped_column(
        DocumentMimeTypesEnum, nullable=False
    )
    file_path: Mapped[str] = mapped_column(nullable=False)
    item_id: Mapped[int | None] = mapped_column(ForeignKey("item.id"), nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    document_type: Mapped[DocumentType | None] = mapped_column(
        Enum(DocumentType, name="document_type_enum"),
        nullable=True,
        default=None,
    )
