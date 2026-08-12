from prompts.generate_python_prompt import generate_python_prompt
from core.llm import non_streaming_llm

generate_python_chain = (
    generate_python_prompt
    |
    non_streaming_llm
)