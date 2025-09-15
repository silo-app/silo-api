from typing import Literal
from silo.schemas.Base import TimestampSchema
from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    filename: str = Field()
    title: str = Field()
    description: str = Field()
    file_size: int = Field()
    mime_type: Literal[
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
    ] = Field(description="Only PDF files and images are allowed.")
    document_type: Literal["manual", "image", "other"] = "other"


class DocumentCreate(DocumentBase):
    item_id: int = Field(description="The Item ID to map the document to")

    class Config:
        json_schema_extra = {
            "example": {
                "filename": "manual_vacuum_cleaner.pdf",
                "title": "Vacum Cleaner Manual",
                "description": "Manual for the vacuum cleaner",
                "file_size": 2097152,
                "mime_type": "application/pdf",
                "document_type": ["manual"],
                "item_id": 23,
            }
        }


class DocumentRead(DocumentBase, TimestampSchema):
    id: int = Field()
    item_id: int = Field()
    user_id: int | None = Field(default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 76,
                "comment": "The item has just been put into storage!",
                "user_id": 3,
                "item_id": 54,
                "created_at": "2025-08-18T16:15:57.123232",
                "updated_at": "2025-08-19T14:24:11.123232",
            }
        }
