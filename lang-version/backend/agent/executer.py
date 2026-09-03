from agent.registry import TOOLS
import traceback

async def execute(
    plan, 
    filters, 
    owner_id,
    image=None
):
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
            tool_input = {
                "filters": filters,
                "owner_id": owner_id,
                "input": step.input
            }

            # For Vision Tool
            
            if step.tool == "vision_tool":
                # Current Image Exists
                if image:
                    image_filename = image["filename"]
                    content_type = image["content_type"]

                # No current image -> use planner's image
                # metadata from conversation history
                else:
                    image_filename = step.input.get("image_filename")
                    content_type = step.input.get("content_type")

                # Make sure planner actually provided image metadata
                if not image_filename or not content_type:
                    raise ValueError(
                        "Vision tool requires image_filename and content_type."
                    )

                tool_input["image_filename"] = image_filename
                tool_input["content_type"] = content_type

                # The actual question
                tool_input["query"] = step.input.get("query", "")

            elif step.tool == "excel_tool":
                # exclude filters for excel_tool
                tool_input.pop("filters", None)

            result = await tool.ainvoke(tool_input)

            print("TOOL RESULT:", result)
            
        except Exception as e:
            traceback.print_exc()

            result = {
                "error": f"Tool '{step.tool}' failed: {e}"
            }

        context[step.tool] = result

    return context