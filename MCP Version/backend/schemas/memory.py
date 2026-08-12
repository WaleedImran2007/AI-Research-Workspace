from pydantic import BaseModel, Field

from datetime import datetime

class MemoryItem(BaseModel):
    type: str | None = None
    key: str | None = None
    value: str | None = None
    importance: float | None = None

class MemoryDecision(BaseModel):
    should_store: bool
    memories: list[MemoryItem] | None = None

class MemoryResponse(BaseModel):
    ownerId: str
    type: str
    key: str
    value: str
    importance: float
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")