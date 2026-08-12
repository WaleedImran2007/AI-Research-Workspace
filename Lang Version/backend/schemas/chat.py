from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    conversation_id: str
    collection_ids: list[str] | None = None