from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class CollectionResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    ownerId: str
    createdAt: Optional[datetime]
    updatedAt: Optional[datetime]