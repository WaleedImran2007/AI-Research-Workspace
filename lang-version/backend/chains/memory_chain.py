from prompts.memory_prompt import memory_prompt
from core.llm import instant_llm
from schemas.memory import MemoryDecision

structured_llm = instant_llm.with_structured_output(
    MemoryDecision,
    method="json_schema"
)

memory_chain = memory_prompt | structured_llm