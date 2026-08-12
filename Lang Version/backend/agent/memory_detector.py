from schemas.memory import MemoryDecision
from chains.memory_chain import memory_chain

def detect_memory(message: str) -> MemoryDecision:
    return memory_chain.invoke(
        {
            "user_query": message
        }
    )