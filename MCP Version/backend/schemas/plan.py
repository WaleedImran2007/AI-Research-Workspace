from pydantic import BaseModel

class PlanStep(BaseModel):
    tool: str
    reason: str
    input: dict = {}

class Plan(BaseModel):
    plan: list[PlanStep]