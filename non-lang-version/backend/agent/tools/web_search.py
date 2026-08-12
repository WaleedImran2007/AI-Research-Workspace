from dotenv import load_dotenv
load_dotenv()

import os
from tavily import TavilyClient

from schemas.tool_result import ToolResult

client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def execute(filters, owner_id, input):
    query = input["query"]

    response = client.search(
        query=query,
        max_results=5
    )

    llm_context = ""
    sources = []

    for result in response["results"]:
        llm_context += f"{result['title']}\n"
        llm_context += f"{result['content']}\n\n"

        sources.append({
            "type": "web",
            "title": result["title"],
            "url": result["url"],
        })

    return ToolResult(
        llm_context=llm_context,
        sources=sources
    )