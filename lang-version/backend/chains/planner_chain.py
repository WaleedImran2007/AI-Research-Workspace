from prompts.planner_prompt import planner_prompt
from core.llm import non_streaming_llm
from schemas.plan import Plan

from langchain_core.output_parsers import PydanticOutputParser

# Create a standard Pydantic parser
parser = PydanticOutputParser(pydantic_object=Plan)

planner_chain = (
    planner_prompt
    |
    non_streaming_llm
    |
    parser
)