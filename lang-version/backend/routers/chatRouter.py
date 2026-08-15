from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from schemas.chat import ChatRequest
from services.query_rewriter import rewrite_query
from services.filter_extractor import extract_filters
from services.metadata_resolver import resolve_filters
from middlewares.authMiddleware import get_current_user

from agent.planner import create_plan
from agent.executer import execute
from agent.synthesizer import synthesize
from agent.reflector import reflect
from agent.intent_detector import detect_intent

from database import messages_collection, conversations_collection
from datetime import datetime, UTC
from bson import ObjectId
from bson.errors import InvalidId

from graph.workflow import graph

import json


router = APIRouter()


MAX_RETRIES = 3

# Post endpoint for chat
@router.post("/")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    # Validate conversation_id
    try:
        conversation_id = ObjectId(request.conversation_id)
    except InvalidId:
        raise HTTPException(
            status_code=400,
            detail="Invalid conversation ID"
        )

    # Check conversation ownership
    conversation = conversations_collection.find_one(
        {
            "_id": conversation_id,
            "ownerId": current_user["id"]
        }
    )

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )


    now = datetime.now(UTC)

    # Load conversation history
    messages = list(
        messages_collection.find(
            {
                "conversation_id": conversation_id
            }
        )
        .sort("createdAt", -1)
        .limit(2)
    )

    messages.reverse()  # Ensure chronological order

    history = []

    for message in messages:
        if message["role"] == "user":
            history.append(
                f'{message["role"].capitalize()}: '
                f'Original Message: {message["content"]} '
                f'Resolved Content: {message["resolved_content"]}'
            )
        else:
            history.append(
                f'{message["role"].capitalize()}: {message["content"]}'
            )

    conversation_history = "\n".join(history)

    initial_state = {
        "user_query": request.query,
        "conversation_history": conversation_history,
        "owner_id": current_user["id"],
        "collection_ids": request.collection_ids,

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

    state = await graph.ainvoke(initial_state)

    answer_generator = state.get("answer")
    sources = state.get("sources") or []

    # Stream response + save final answer
    def stream_answer():
        full_answer = ""

        for token in answer_generator:
            full_answer += token
            payload = json.dumps({"type": "token", "content": token})
            yield f"data: {payload}\n\n"

        # send sources after answer completes
        payload = json.dumps({"type": "sources", "content": sources})
        yield f"data: {payload}\n\n"

        messages_collection.insert_many([
            {
                "conversation_id": conversation_id,
                "role": "user",
                "content": request.query,
                "resolved_content": state.get("search_query", request.query),
                "createdAt": now
            },

            {
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": full_answer,
                "sources": sources,
                "createdAt": datetime.now(UTC)
            }
        ])


        # Update conversation timestamp
        conversations_collection.update_one(
            {
                "_id": conversation_id
            },
            {
                "$set": {
                    "updatedAt": datetime.now(UTC)
                }
            }
        )


    return StreamingResponse(
        stream_answer(),
        media_type="text/event-stream"
    )
