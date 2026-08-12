from schemas.tool_result import ToolResult

from langchain_core.tools import tool

from mcp_manager.manager import mcp_manager

@tool
async def web_search(filters, owner_id, input) -> ToolResult:
    """Performs a web search based on the provided query in the input and returns the results."""

    query = input["query"]
    max_results = input.get("max_results", 5)
    search_depth = input.get("search_depth", "basic")

    response = await mcp_manager.call_tool(
        server_name = "web_search",
        tool_name = "web_search",
        arguments = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth
        }
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