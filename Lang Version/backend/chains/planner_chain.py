from prompts.planner_prompt import planner_prompt
from core.llm import non_streaming_llm
from schemas.plan import Plan

structured_llm = non_streaming_llm.with_structured_output(Plan)

planner_chain = (
    planner_prompt
    |
    structured_llm
)