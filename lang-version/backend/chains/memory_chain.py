from prompts.memory_prompt import memory_prompt
from core.llm import non_streaming_llm
from schemas.memory import MemoryDecision

structured_llm = non_streaming_llm.with_structured_output(MemoryDecision)
memory_chain = memory_prompt | structured_llm