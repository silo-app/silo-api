from pathlib import Path
import uuid
import aiofiles

from fastapi import HTTPException, UploadFile

from silo import config
from silo.schemas.Document import DocumentMimeTypes


class DocumentManager:
    def __init__(self):
        self.upload_directory = Path(config.document_upload_directory)
        self.upload_directory.mkdir(exist_ok=True)

        self.max_file_size = config.document_max_file_size

    async def validate(self, file: UploadFile) -> dict:
        content = await file.read()
        await file.seek(0)

        if len(content) > self.max_file_size:
            raise HTTPException(
                status_code=413, detail="Document size exceeds the upload limit"
            )

        try:
            DocumentMimeTypes(file.content_type)
        except ValueError:
            raise HTTPException(
                status_code=400, detail=f"Document type {file.content_type} not allowed"
            )

        return {
            "content": content,
            "size": len(content),
            "mime_type": file.content_type,
            "filename": file.filename,
        }

    async def save(self, file: UploadFile) -> str:
        fdata = await self.validate(file)
        extension = Path(fdata["filename"]).suffix
        filename = f"{str(uuid.uuid4())}{extension}"
        filepath = self.upload_directory / filename

        async with aiofiles.open(filepath, "wb") as filebuffer:
            await filebuffer.write(fdata["content"])

        return str(filepath.relative_to(self.upload_directory))

    async def delete(self, filepath: str) -> bool:
        ffilepath = self.upload_directory / filepath

        if ffilepath.exists():
            ffilepath.unlink()
            return True

        return False
