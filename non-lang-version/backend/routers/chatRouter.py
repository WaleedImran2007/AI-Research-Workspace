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

import json


router = APIRouter()


MAX_RETRIES = 3

# Post endpoint for chat
@router.post("/")
def chat(
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
        ).sort("createdAt", 1)
    )

    history = []

    for message in messages:
        history.append(
            f'{message["role"].capitalize()}: {message["content"]}'
        )

    conversation_history = "\n".join(history)

    # Save user message
    messages_collection.insert_one(
        {
            "conversation_id": conversation_id,
            "role": "user",
            "content": request.query,
            "createdAt": now
        }
    )

    # if user is just greeting, respond with a simple greeting without invoking the planner or tools

    intent_result = detect_intent(request.query)

    print("Detected Intent:", intent_result)

    if intent_result["intent"] == "greeting":

        print("Detected greeting intent. Responding with a simple greeting.")

        def stream_greeting():
            answer = "Hello! How can I help you today?"

            full_answer = ""

            for token in answer.split():
                token += " "
                full_answer += token

                payload = json.dumps({
                    "type": "token",
                    "content": token
                })

                yield f"data: {payload}\n\n"


            payload = json.dumps({
                "type": "sources",
                "content": []
            })

            yield f"data: {payload}\n\n"


            # Save assistant message if needed
            messages_collection.insert_one(
                {
                    "conversation_id": conversation_id,
                    "role": "assistant",
                    "content": full_answer,
                    "sources": [],
                    "createdAt": datetime.now(UTC)
                }
            )


        return StreamingResponse(
            stream_greeting(),
            media_type="text/event-stream"
        )

    # Rewrite query for follow-up questions
    search_query = request.query

    if conversation_history:
        search_query = rewrite_query(
            query=request.query,
            history=conversation_history
        )

    # Extract + resolve filters (used by the retrieval / page_loader tools)
    filters = extract_filters(search_query)
    print("Extracted Filters:", filters)

    resolved_filters = resolve_filters(filters, owner_id=current_user["id"])

    # Merge in any collection scoping the client passed explicitly
    if request.collection_ids:
        resolved_filters.collection_ids = list(
            set(resolved_filters.collection_ids) | set(request.collection_ids)
        )

    print("Resolved Filters:", resolved_filters)

    retry_count = 0
    feedback = None

    plan = None
    context = None
    reflection = None

    while retry_count < MAX_RETRIES:
        print(f"--- Attempt {retry_count + 1} ---")

        try:
            # Plan which tool(s) should run for this query
            if plan is None or (reflection and reflection.action == "replan"):
                plan = create_plan(
                    search_query, 
                    feedback=feedback,
                    previous_plan=plan,
                )

                print("Plan:", plan)

            # Execute the planned tools (retrieval, page_loader, calculator, web_search)
            context = execute(
                plan=plan,
                filters=resolved_filters,
                owner_id=current_user["id"]
            )

            # Reflect on the answer to ensure it is appropriate and accurate
            reflection = reflect(
                user_query=search_query,
                plan=plan,
                context=context
            )

            print(f"Reflection Approved: {reflection.approved} | Reason: {reflection.reason}")

            if reflection.approved:
                break

            if reflection.action == "replan":
                plan = None  # Force replan on next iteration
                feedback = f"""
                    Previous Plan Failed

                    Reason: {reflection.reason}
                    Suggested Action: {reflection.action}
                """

            elif reflection.action == "retry_tool":
                pass  # No action needed, will retry the same tool

            elif reflection.action == "stop":
                break  # Stop processing further, return what we have

            retry_count += 1

        except Exception as e:
            retry_count += 1
            print(f"Attempt {retry_count} failed: {e}")
            if retry_count >= MAX_RETRIES:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to process query after {MAX_RETRIES} attempts."
                )

    if reflection and not reflection.approved:
        def failed():
            yield (
                "I couldn't confidently answer your question after "
                "multiple attempts. Please try rephrasing it."
            )

        return StreamingResponse(
            failed(),
            media_type="text/event-stream"
        )


    # Synthesize the final answer from the aggregated tool context
    answer_generator, sources = synthesize(
        user_query=search_query,
        context=context,
        history=conversation_history,
        reflection=reflection
    )

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

        # Save completed assistant message
        messages_collection.insert_one(
            {
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": full_answer,
                "sources": sources,
                "createdAt": datetime.now(UTC)
            }
        )


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
