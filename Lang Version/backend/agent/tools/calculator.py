from schemas.tool_result import ToolResult

from langchain_core.tools import tool

from sympy import sympify

@tool
async def calculator(filters, owner_id, input) -> ToolResult:
    """Evaluates a mathematical expression provided in the input and returns the result."""

    expression = input["expression"]

    # USING SYMPY
    result = sympify(expression).evalf()

    result_str = str(result)

    if "." in result_str:
        # Remove trailing zeros and the decimal point if it's an integer
        result_str = result_str.rstrip('0').rstrip('.')

    return ToolResult(
        llm_context = f"The result of the expression '{expression}' is: {result_str}",
        sources = []
    )