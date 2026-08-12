from pydantic import BaseModel

class Intent(BaseModel):
    intent: str
    needs_planner: bool