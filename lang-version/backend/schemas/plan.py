from pydantic import BaseModel, Field


class PlanStep(BaseModel):

    tool: str = Field(
        description=(
            "The name of the tool to execute. "
            "Examples: 'retrieval', 'python_tool', "
            "'web_search', 'vision_tool', 'excel_tool'."
        )
    )

    reason: str = Field(
        description="Explanation of why this tool was chosen."
    )

    input: dict = Field(
        default_factory=dict,
        description="Arguments required by the selected tool."
    )


class Plan(BaseModel):

    """Execution plan containing sequential tool steps."""

    plan: list[PlanStep] = Field(
        description="List of plan steps to execute sequentially."
    )