from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from core.supabase import supabase

router = APIRouter()

@router.get("/{filename}")
async def get_ai_image(filename: str):
    storage_path = f"chat-images/{filename}"

    try:
        image_bytes = (
            supabase.storage
            .from_("airw-documents")
            .download(storage_path)
        )

    except Exception as e:
        print("Supabase image download error:", e)

        raise HTTPException(
            status_code=404,
            detail="AI image not found"
        )

    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": "inline"
        }
    )