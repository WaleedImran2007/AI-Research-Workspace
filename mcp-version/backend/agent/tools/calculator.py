from schemas.tool_result import ToolResult

from langchain_core.tools import tool

from mcp_manager.manager import mcp_manager

@tool
async def calculator(filters, owner_id, input) -> ToolResult:
    """Evaluates a mathematical expression provided in the input and returns the result."""

    expression = input["expression"]

    result = await mcp_manager.call_tool(
        server_name = "calculator",
        tool_name = "calculator",
        arguments = {
            "expression": expression
        }
    )

    return ToolResult(
        llm_context = f"The result of the expression '{expression}' is: {result}",
        sources = []
    )