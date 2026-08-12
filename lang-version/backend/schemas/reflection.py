from pydantic import BaseModel

class Reflection(BaseModel):
    approved: bool
    action: str | None = None
    reason: str