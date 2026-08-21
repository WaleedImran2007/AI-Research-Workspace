from dotenv import load_dotenv
load_dotenv()

import os
from langchain_groq import ChatGroq

non_streaming_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY"),
)

streaming_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY"),
    streaming=True
)

instant_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.environ.get("GROQ_API_KEY"),
)