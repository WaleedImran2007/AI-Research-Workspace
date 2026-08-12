from pydantic import BaseModel, Field
from datetime import datetime
from schemas.message import MessageResponse

class ConversationCreate(BaseModel):
    pass

class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: list[MessageResponse]

class UpdateConversationRequest(BaseModel):
    title: str