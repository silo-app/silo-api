from typing import Annotated, Literal
from fastapi import Depends, APIRouter, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from silo.api.dependencies import get_current_user, require_permission
from silo.database import async_get_db
from silo.database import models
from silo.schemas import DocumentCreate, DocumentUpdate, DocumentRead, DocumentMimeTypes
from silo.schemas.Document import DocumentType
from silo.schemas.User import UserRead
from silo.utils import DocumentManager

doc_manager = DocumentManager()

document_router = APIRouter(
    tags=["Document"], dependencies=[Depends(require_permission())]
)


@document_router.get(
    "/document/",
    summary="Get all Documents",
    response_model=list[DocumentRead],
)
@document_router.get(
    "/document/{id}",
    summary="Get a specific Document",
    response_model=DocumentRead,
)
async def get_documents(
    session: AsyncSession = Depends(async_get_db), id: int | None = None
) -> DocumentRead | list[DocumentRead]:
    if id is not None:
        result = await session.scalars(
            select(models.Document).where(models.Document.id == id)
        )
        comment = result.one_or_none()

        if comment is not None:
            return DocumentRead.model_validate(comment, from_attributes=True)

        raise HTTPException(status_code=404, detail=f"Document {id} not found")

    result = await session.scalars(select(models.Document))
    comments = result.all()

    return [
        DocumentRead.model_validate(comment, from_attributes=True)
        for comment in comments
    ]


@document_router.post(
    "/document/",
    summary="Upload a new Document",
    response_model=DocumentRead,
    status_code=201,
)
async def new_document(
    file: Annotated[UploadFile, File(description="Document file to upload")],
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
    session: AsyncSession = Depends(async_get_db),
    user: UserRead = Depends(get_current_user),
) -> DocumentRead:
    file_metadata = await doc_manager.validate(file)
    file_path = await doc_manager.save(file)

    document_create = DocumentCreate(
        filename=file.filename,
        title=title,
        description=description,
        file_size=file_metadata["size"],
        mime_type=DocumentMimeTypes(file_metadata["mime_type"]),
        document_type=document_type,
        item_id=item_id,
        file_path=file_path,
        user_id=user.id,
    )

    new_document = models.Document(**document_create.model_dump())
    session.add(new_document)
    await session.commit()
    await session.refresh(new_document)

    return DocumentRead.model_validate(new_document, from_attributes=True)


@document_router.put(
    "/document/{id}",
    summary="Update an existing Document",
    status_code=204,
)
async def update_comment(
    id: int,
    title: Annotated[
        str, Form(min_length=1, max_length=255, description="Document title")
    ],
    description: Annotated[
        str, Form(min_length=1, max_length=1000, description="Document description")
    ],
    document_type: Annotated[
        Literal["manual", "image", "other"], Form(description="Document type")
    ] = "other",
    session: AsyncSession = Depends(async_get_db),
):
    document = await session.get(models.Document, id)
    if document is None:
        raise HTTPException(404, detail="Document not found")

    document_update = DocumentUpdate(
        title=title,
        description=description,
        document_type=document_type,
    )
    update_data = document_update.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        if hasattr(document, field):
            if field == "document_type" and isinstance(value, str):
                setattr(document, field, DocumentType(value))
            else:
                setattr(document, field, value)

    await session.commit()


@document_router.delete(
    "/document/{id}",
    summary="Delete a Document",
    status_code=204,
)
async def delete_document(id: int, session: AsyncSession = Depends(async_get_db)):
    document = await session.get(models.Document, id)
    if document is None:
        raise HTTPException(404, detail="Document not found")

    await session.delete(document)
    await session.commit()
