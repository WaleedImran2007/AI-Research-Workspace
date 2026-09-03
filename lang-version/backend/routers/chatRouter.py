from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Form, File, UploadFile, 
    Response
)

from fastapi.responses import StreamingResponse

from schemas.chat import ChatRequest

from middlewares.authMiddleware import get_current_user

from database import messages_collection, conversations_collection, users_collection

from bson import ObjectId
from bson.errors import InvalidId

from graph.workflow import graph

from core.supabase import supabase

from uuid import uuid4
import mimetypes
import json
import asyncio

from datetime import datetime, UTC, timedelta, timezone
from zoneinfo import ZoneInfo

from pymongo import ReturnDocument

router = APIRouter()

MAX_RETRIES = 3

NODE_STATUS_LABELS = {
    "intent": "Understanding your question...",
    "rewrite": "Refining the search query...",
    "extract_filters": "Extracting filters...",
    "planner": "Planning how to answer...",
    "executer": "Searching your documents...",
    "reflection": "Checking the results...",
}

_SENTINEL = object()

async def _aiter_sync(iterable):
    """
    Bridge a blocking/sync iterator (e.g. synthesizer_chain.stream(), or a
    plain string from greeting/direct_answer) into an async iterator
    without blocking the event loop. Each `next()` call - which may involve
    a blocking network read from Groq - runs in a worker thread.
    """
    it = iter(iterable)

    while True:
        item = await asyncio.to_thread(next, it, _SENTINEL)

        if item is _SENTINEL:
            break

        yield item


# Post endpoint for chat
@router.post("/")
async def chat(
    query: str = Form(...),
    conversation_id: str = Form(...),
    collection_ids: str | None = Form(None),
    web_enabled: bool = Form(False),
    image: UploadFile | None = File(None),
    current_user: dict = Depends(get_current_user)
):

    PAKISTAN_TZ = ZoneInfo("Asia/Karachi")

    # Fetch User
    user = users_collection.find_one(
        {"_id": ObjectId(current_user["id"])}
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    now_pk = datetime.now(PAKISTAN_TZ)
    reset_date = user.get("aiResetDate")

    # Normalize reset_date to PKT offset-aware datetime
    if reset_date:
        if reset_date.tzinfo is None:
            reset_date = reset_date.replace(tzinfo=timezone.utc)
        reset_date_pk = reset_date.astimezone(PAKISTAN_TZ)
    else:
        reset_date_pk = None

    # Compare using the normalized PKT timezone
    if reset_date_pk and now_pk >= reset_date_pk:
        next_midnight_pk = (
            now_pk.replace(hour=0, minute=0, second=0, microsecond=0) 
            + timedelta(days=1)
        )

        user = users_collection.find_one_and_update(
            {"_id": ObjectId(current_user["id"])},
            {
                "$set": {
                    "aiRequestsRemaining": 15,
                    "aiResetDate": next_midnight_pk
                }
            },
            return_document=ReturnDocument.AFTER
        )

    def stream_no_requests():
        payload = json.dumps({
            "type": "token",
            "content": "You have no AI requests remaining. Please wait until your quota resets."
        })
        yield f"data: {payload}\n\n"

        payload = json.dumps({
            "type": "sources",
            "content": []
        })
        yield f"data: {payload}\n\n"

    # Block request if quota is depleted
    if user.get("aiRequestsRemaining", 0) <= 0:
        return StreamingResponse(
            stream_no_requests(),
            media_type="text/event-stream"
        )

    # Deduct 1 request
    users_collection.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$inc": {"aiRequestsRemaining": -1}}
    )
    

    print("Web Enabled:", web_enabled)

    # ==================================================
    # PARSE COLLECTION IDS
    # ==================================================

    if collection_ids:
        try:
            collection_ids = json.loads(collection_ids)

        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid collection_ids format"
            )

    else:
        collection_ids = []


    # ==================================================
    # VALIDATE CONVERSATION ID
    # ==================================================

    try:
        conversation_id = ObjectId(conversation_id)

    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID"
        )


    # ==================================================
    # CHECK CONVERSATION OWNERSHIP
    # ==================================================

    conversation = conversations_collection.find_one({
        "_id": conversation_id,
        "ownerId": current_user["id"]
    })

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )


    now = datetime.now(UTC)


    # ==================================================
    # LOAD RECENT CONVERSATION HISTORY
    # ==================================================

    messages = list(
        messages_collection.find(
            {
                "conversation_id": conversation_id
            }
        )
        .sort("createdAt", -1)
        .limit(2)
    )

    messages.reverse()


    history = []

    for message in messages:

        if message["role"] == "user":

            image_info = ""

            if message.get("image"):
                image_info = (
                    f' Image attached: {message["image"]}'
                )

            history.append(
                f'User: '
                f'Original Message: {message["content"]} '
                f'Resolved Content: '
                f'{message.get("resolved_content", message["content"])}'
                f'{image_info}'
            )

        else:

            history.append(
                f'Assistant: {message["content"]}'
            )


    conversation_history = "\n".join(history)


    # ==================================================
    # CURRENT IMAGE
    # ==================================================

    image_data = None
    image_bytes = None
    image_content_type = None

    if image:

        print("IMAGE RECEIVED:")
        print("Filename:", image.filename)
        print("Content type:", image.content_type)

        image_bytes = await image.read()

        print("Image size:", len(image_bytes))

        # Generate unique filename
        image_filename = f"{uuid4().hex}_{image.filename}"

        storage_path = f"chat-images/{image_filename}"

        # --------------------------------------------------
        # Upload image to Supabase
        # --------------------------------------------------

        try:

            supabase.storage.from_("airw-documents").upload(
                storage_path,
                image_bytes,
                {
                    "content-type": image.content_type
                }
            )

            print("IMAGE UPLOADED:", storage_path)


            # --------------------------------------------------
            # Store image metadata in state
            # --------------------------------------------------

            image_data = {
                "filename": image_filename,
                "content_type": image.content_type,
            }


        except Exception as e:
            print("Supabase image upload error:", e)
            image_data = None

    # ==================================================
    # INITIAL AGENT STATE
    # ==================================================

    initial_state = {
        # User
        "user_query": query,
        "conversation_history": conversation_history,
        "search_query": query,

        # User / Collections
        "owner_id": current_user["id"],
        "collection_ids": collection_ids,

        "web_enabled": web_enabled,

        # Image Information
        "image": image_data,

        "memories": None,

        "retry_count": 0,

        "feedback": None,
        "plan": None,
        "intent": None,

        "filters": None,
        "resolved_filters": None,

        "context": None,

        "reflection": None,
        "answer": None,
        "sources": [],

    }

    # ==================================================
    # STREAM: run the graph node-by-node via astream() instead of a single
    # blocking ainvoke(). Each node's completion is turned into an SSE
    # "status" event so the client gets its first byte almost immediately,
    # instead of waiting for the whole pipeline (intent -> planner ->
    # retrieval -> reflection) to finish silently before anything streams.
    # Once the terminal node (greeting / direct_answer / synthesizer) sets
    # "answer" in the state, we switch to streaming its tokens.
    # ==================================================

    async def event_stream():

        final_state = dict(initial_state)
        answer_source = None
        sources = []

        async for step in graph.astream(initial_state, stream_mode="updates"):
            for node_name, node_update in step.items():
                if not node_update:
                    continue

                final_state.update(node_update)

                label = NODE_STATUS_LABELS.get(node_name)

                if label:
                    payload = json.dumps({
                        "type": "status",
                        "content": label
                    })

                    yield f"data: {payload}\n\n"

                if "answer" in node_update and node_update["answer"] is not None:
                    answer_source = node_update["answer"]

                if "sources" in node_update and node_update["sources"]:
                    sources = node_update["sources"]

        if answer_source is None:
            answer_source = final_state.get("answer") or ""

        sources = final_state.get("sources") or sources or []

        generated_file = None

        context = final_state.get("context") or {}

        excel_result = context.get("excel_tool")

        if excel_result:
            if hasattr(excel_result, "file"):
                generated_file = excel_result.file
            elif isinstance(excel_result, dict):
                generated_file = excel_result.get("file")

        full_answer = ""

        # Stream answer tokens (works whether answer_source is the
        # synthesizer's generator, or a plain string from greeting /
        # direct_answer - matches the previous behaviour exactly).

        async for token in _aiter_sync(answer_source):

            full_answer += token

            payload = json.dumps({
                "type": "token",
                "content": token
            })

            yield f"data: {payload}\n\n"

        # Send sources
        file_data = None

        if generated_file:
            file_data = {
                "filename": generated_file.filename,
                "type": generated_file.file_type,
                "storagePath": generated_file.storage_path
            }

        payload = json.dumps({
            "type": "sources",
            "content": sources,
            "file": file_data
        })

        yield f"data: {payload}\n\n"

        # Save user message

        user_message = {
            "conversation_id": conversation_id,
            "role": "user",
            "content": query,

            "resolved_content": final_state.get(
                "search_query",
                query
            ),

            "createdAt": now
        }


        # Save image filename only

        if image_data:
            user_message["image"] = (
                image_data["filename"]
            )


        # Save assistant message

        assistant_message = {
            "conversation_id": conversation_id,
            "role": "assistant",
            "content": full_answer,
            "sources": sources,
            "createdAt": datetime.now(UTC)
        }

        if generated_file:
            assistant_message["file"] = {
                "filename": generated_file.filename,
                "type": generated_file.file_type,
                "storagePath": generated_file.storage_path
            }

        await asyncio.to_thread(
            messages_collection.insert_many,
            [user_message, assistant_message]
        )

        # --------------------------------------------------
        # Update conversation timestamp
        # --------------------------------------------------

        await asyncio.to_thread(
            conversations_collection.update_one,
            {"_id": conversation_id},
            {"$set": {"updatedAt": datetime.now(UTC)}}
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


# New — serves persisted chat images, same pattern as your PDF viewer
@router.get("/images/{filename}")
def view_chat_image(filename: str):
    storage_path = f"chat-images/{filename}"

    try:
        file_bytes = supabase.storage.from_("airw-documents").download(storage_path)
    except Exception as e:
        print("Supabase download error:", e)
        raise HTTPException(status_code=404, detail="Image not found in storage.")

    media_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={"Content-Disposition": "inline"}
    )

@router.get("/documents/{filename}")
def view_chat_document(filename: str):
    storage_path = f"chat-documents/{filename}"

    try:
        file_bytes = supabase.storage.from_("airw-documents").download(storage_path)
    except Exception as e:
        print("Supabase download error:", e)
        raise HTTPException(status_code=404, detail="Document not found in storage.")

    media_type = (
        mimetypes.guess_type(filename)[0]
        or "application/octet-stream"
    )

    return Response(
        content=file_bytes,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )