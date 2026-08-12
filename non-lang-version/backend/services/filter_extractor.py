from dotenv import load_dotenv
load_dotenv()

import os
import json
from groq import Groq
from schemas.filter import FilterSchema

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_filters(query:str) -> FilterSchema:
    prompt = f"""
        You are an AI Assistant that extracts filters from a user's query. 

        RULES:
        - Preserve the user's query exactly.
        - Do NOT rewrite, summarize, expand, infer, or add context.
        - Only remove the words that represent filters
        (document names, collection names, pages).
        - Never add new concepts.

        Return only valid JSON

        Schema: 
        {{
            "query": str,
            "document_names": list[str],
            "collection_names": list[str],
            "pages": list[int]
        }}

        Examples:

        User:
        Explain transactions from Lecture 2

        Output:
        {{
            "query": "Explain transactions",
            "document_names": ["Lecture 2"],
            "collection_names": [],
            "pages": []
        }}

        User:
        Compare ACID from Lecture 2 and Lecture 5

        Output:
        {{
            "query": "Compare ACID",
            "document_names": ["Lecture 2", "Lecture 5"],
            "collection_names": [],
            "pages": []
        }}

        User:
        Explain normalization from page 8

        Output:
        {{
            "query": "Explain normalization",
            "document_names": [],
            "collection_names": [],
            "pages": [8]
        }}

        User:
        What is a transaction and data Model

        Output:
            {{
                "query": "What is a transaction and data Model",
                "document_names": [],
                "collection_names": [],
                "pages": []
            }}
        

        User Query:
        {query}
    """

    response = client.chat.completions.create(
        model = "llama-3.3-70b-versatile",
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature = 0,
        response_format = {"type": "json_object"}
    )

    print(response.choices[0].message.content)
    data = json.loads(response.choices[0].message.content)

    filters = FilterSchema.model_validate(data)
    return filters