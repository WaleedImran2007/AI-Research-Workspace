from prompts.reflector_prompt import reflector_prompt
from schemas.reflection import Reflection
from core.llm import instant_llm

structured_llm = instant_llm.with_structured_output(
    Reflection,
    method="json_schema"
)

reflector_chain = (
    reflector_prompt
    |
    structured_llm
)