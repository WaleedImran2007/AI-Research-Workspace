from core.vision import analyze_image

from schemas.tool_result import ToolResult

from langchain_core.tools import tool

from core.supabase import supabase

@tool
async def vision_tool(
    image_filename: str,
    content_type: str,
    query: str
) -> ToolResult:
    
    """
    Analyze an image using the vision model.
    """

    storage_path = f"chat-images/{image_filename}"

    try:
        image_bytes = supabase.storage.from_(
            "airw-documents"
        ).download(storage_path)
        
    except Exception as e:
        return ToolResult(
            llm_context = f"Failed to retrieve Image: {str(e)}",
            sources = [],
        )

    answer = await analyze_image(
        image_bytes=image_bytes,
        content_type=content_type,
        query=query
    )

    return ToolResult(
        llm_context = answer,
        sources = []
    )