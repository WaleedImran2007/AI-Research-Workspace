from sympy import sympify
from schemas.tool_result import ToolResult

def execute(filters, owner_id, input):
    expression = input["expression"]

    # USING SYMPY
    result = sympify(expression).evalf()

    return ToolResult(
        llm_context = f"The result of the expression '{expression}' is: {result}",
        sources = []
    )