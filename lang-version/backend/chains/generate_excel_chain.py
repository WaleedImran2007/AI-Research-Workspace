from core.llm import non_streaming_llm
from prompts.generate_excel_prompt import generate_excel_prompt

generate_excel_chain = (
    generate_excel_prompt
    |
    non_streaming_llm
)