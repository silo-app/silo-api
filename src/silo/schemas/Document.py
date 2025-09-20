from typing import Annotated, Literal
from enum import Enum
from fastapi import Form
from pydantic import BaseModel, Field

from silo.schemas.Base import TimestampSchema


class DocumentType(Enum):
    MANUAL = "manual"
    IMAGE = "image"
    OTHER = "other"


class DocumentMimeTypes(Enum):
    PDF = "application/pdf"
    JPEG = "image/jpeg"
    JPG = "image/jpg"
    PNG = "image/png"


def document_form_data(
    title: Annotated[
        str, Form(min_length=1, max_length=255, description="Document title")
    ],
    description: Annotated[
        str, Form(min_length=1, max_length=1000, description="Document description")
    ],
    item_id: Annotated[
        int, Form(gt=0, description="The Item ID to map the document to")
    ],
    document_type: Annotated[
        Literal["manual", "image", "other"], Form(description="Document type")
    ] = "other",
):
    return {
        "title": title,
        "description": description,
        "document_type": document_type,
        "item_id": item_id,
    }


class DocumentBase(BaseModel):
    filename: str = Field()
    title: str = Field()
    description: str = Field()
    file_size: int = Field(gt=0)
    mime_type: DocumentMimeTypes
    document_type: DocumentType
    file_path: str = Field(max_length=500)


class DocumentCreate(DocumentBase):
    item_id: int = Field(gt=0)
    user_id: int | None = Field(default=None)


class DocumentUpdate(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    document_type: Literal["manual", "image", "other"] | None = None


class DocumentRead(DocumentBase, TimestampSchema):
    id: int
    item_id: int
    user_id: int | None
