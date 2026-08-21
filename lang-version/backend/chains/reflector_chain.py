from prompts.reflector_prompt import reflector_prompt
from schemas.reflection import Reflection
from core.llm import non_streaming_llm

structured_llm = non_streaming_llm.with_structured_output(
    Reflection,
    method="json_schema"
)

reflector_chain = (
    reflector_prompt
    |
    structured_llm
)