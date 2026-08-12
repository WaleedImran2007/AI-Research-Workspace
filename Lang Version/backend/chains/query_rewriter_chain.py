from langchain_core.output_parsers import StrOutputParser
from prompts.query_rewriter_prompt import query_rewriter_prompt
from core.llm import instant_llm

query_rewriter_chain = (
    query_rewriter_prompt
    |
    instant_llm
    |
    StrOutputParser()
)