from prompts.intent_prompt import intent_prompt
from schemas.intent import Intent
from core.llm import instant_llm

structured_llm = instant_llm.with_structured_output(
    Intent,
    method="json_schema"
)

intent_chain = (
    intent_prompt
    |
    structured_llm
)