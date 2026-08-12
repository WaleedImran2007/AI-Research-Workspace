from prompts.synthesizer_prompt import synthesizer_prompt
from core.llm import streaming_llm

synthesizer_chain = (
    synthesizer_prompt 
    | 
    streaming_llm
)