from typing import TypedDict, Generator

from schemas.intent import Intent
from schemas.plan import Plan
from schemas.reflection import Reflection
from schemas.filter import FilterSchema
from schemas.memory import MemoryResponse

class AgentState(TypedDict):
    user_query: str
    conversation_history: str | None

    memories: list[MemoryResponse] | None

    owner_id: str
    collection_ids: list[str] | None

    search_query: str

    intent: Intent | None

    filters: FilterSchema | None
    resolved_filters: FilterSchema | None

    plan: Plan | None
    context: dict | None

    reflection: Reflection | None
    feedback: str | None
    retry_count: int

    answer: Generator[str, None, None] | None
    sources: list[dict] | None