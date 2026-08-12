from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: str
    ownerId: str
    collectionId: str

    originalName: str
    fileName: str

    mimeType: str
    documentType: Optional[str] = None  # e.g., "pdf", "csv", etc.
    filesize: int

    status: str

    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]
