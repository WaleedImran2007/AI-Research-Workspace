from agent.registry import TOOLS
import traceback

async def execute(plan, filters, owner_id):
    context = {}

    for step in plan.plan:
        # Avoid running the same tool twice if the planner repeats itself
        if step.tool in context:
            continue

        tool = TOOLS.get(step.tool)

        if tool is None:
            context[step.tool] = {"error": f"Unknown tool: {step.tool}"}
            continue

        try:
            result = await tool.ainvoke(
                {
                    "filters": filters,
                    "owner_id": owner_id,
                    "input": step.input
                }
            )
            
        except Exception as e:
            result = {"error": f"Tool '{step.tool}' failed: {e}"}
            traceback.print_exc()

            result = {
                "error": str(e)
            }

        context[step.tool] = result

    return context