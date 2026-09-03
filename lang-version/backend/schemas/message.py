from typing import Any

from pydantic import BaseModel, Field
from datetime import datetime

class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    sources: list = Field(default_factory=list)
    image: str | None = None
    file: dict[str, Any] | None = None
    created_at: datetime = Field(..., alias="createdAt")