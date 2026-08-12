from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, UTC
from database import conversations_collection, messages_collection
from middlewares.authMiddleware import get_current_user
from schemas.conversation import ConversationResponse, ConversationDetailResponse, UpdateConversationRequest
from utils.serializer import conversation_serializer, conversations_serializer, message_serializer, messages_serializer

from bson import ObjectId
from bson.errors import InvalidId

router = APIRouter()

# POST REQUEST: Create a new conversation
@router.post("/", response_model=ConversationResponse)
def create_conversation(
    current_user: dict = Depends(get_current_user)
):
    now = datetime.now(UTC)
    new_conversation = {
        "ownerId": current_user["id"],
        "title": "new chat",
        "createdAt": now,
        "updatedAt": now
    }

    result = conversations_collection.insert_one(new_conversation)

    new_conversation["_id"] = str(result.inserted_id)

    return conversation_serializer(new_conversation)

# GET REQUEST: Get all conversations for the current user
@router.get("/", response_model=list[ConversationResponse])
def get_conversations(
    current_user: dict = Depends(get_current_user)
):
    conversations = conversations_collection.find({"ownerId": current_user["id"]}).sort("updatedAt", -1)

    return conversations_serializer(list(conversations))

# GET: Load a specific conversation by ID
@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        conversation_id = ObjectId(conversation_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    conversation = conversations_collection.find_one({"_id": conversation_id, "ownerId": current_user["id"]})

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    messages = list(messages_collection.find({"conversation_id": conversation_id}).sort("createdAt", 1))
    
    return {
        "conversation": conversation_serializer(conversation),
        "messages": messages_serializer(messages)
    }

# PATCH: UPDATE CONVERSATION NAME
@router.patch("/{conversation_id}", response_model=ConversationResponse)
def update_conversation(
    conversation_id: str,
    payload: UpdateConversationRequest,
    current_user: dict = Depends(get_current_user)
):
    try:
        conversation_id = ObjectId(conversation_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    updated_conversation = conversations_collection.find_one_and_update(
        {"_id": conversation_id},
        {"$set": {"title": payload.title, "updatedAt": datetime.now(UTC)}},
        return_document=True
    )

    if not updated_conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation_serializer(updated_conversation)

# DELETE: DELETE A CONVERSATION AND IT'S MESSAGES
@router.delete("/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        conversation_id = ObjectId(conversation_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    deleted_conversation = conversations_collection.find_one_and_delete(
        {"_id": conversation_id, "ownerId": current_user["id"]}
    )

    if not deleted_conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    deleted_messages = messages_collection.delete_many({"conversation_id": conversation_id})

    return {
        "message": "Conversation and its messages deleted successfully",
        "deletedMessagesCount": deleted_messages.deleted_count
    }