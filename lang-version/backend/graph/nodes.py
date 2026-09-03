import asyncio
import threading

from graph.state import AgentState

from utils.embedder import create_embedding
from utils.memory_retrieval import retrieve_memories

from services.query_rewriter import rewrite_query
from services.filter_extractor import extract_filters
from services.metadata_resolver import resolve_filters

from agent.intent_detector import detect_intent
from agent.planner import create_plan
from agent.executer import execute
from agent.reflector import reflect
from agent.synthesizer import synthesize
from agent.memory_detector import detect_memory
from agent.direct_response import direct_response_chain

from schemas.memory import MemoryResponse

from database import memories_collection

from datetime import datetime, UTC

MAX_RETRIES = 3

# Keep strong references to fire-and-forget memory tasks so they aren't
# garbage-collected mid-flight (asyncio only holds a weak reference).

_background_memory_tasks: set[asyncio.Task] = set()

def _store_memories_sync(user_query: str, owner_id: str) -> None:
    decision = detect_memory(user_query)

    print("Decision: ", decision)
    
    if not decision.should_store:
        return

    now = datetime.now(UTC)

    for item in decision.memories:
        memory_text = (
            f"The user's {item.key.replace('_', ' ')} "
            f"is {item.value}."
        )

        embedding = create_embedding(memory_text)

        memories_collection.update_one(
            {
                "ownerId": owner_id,
                "key": item.key
            },
            {
                "$set": {
                    "type": item.type,
                    "value": item.value,
                    "importance": item.importance,
                    "memory_text": memory_text,
                    "embedding": embedding,
                    "updatedAt": now
                },

                "$setOnInsert": {
                    "ownerId": owner_id,
                    "createdAt": now
                },
            },

            upsert=True
        )

def memory_node(state: AgentState):
    user_query = state.get("user_query", "")

    threading.Thread(
        target = _store_memories_sync,
        args = (user_query, state["owner_id"]),
        daemon = True
    ).start()

    return {}
    

def intent_node(state: AgentState):
    user_query = state.get("user_query", "")
    intent = detect_intent(user_query)

    return {
        "intent": intent
    }

def route_after_intent(state: AgentState):
    if not state["intent"].needs_planner:
        if state["intent"].intent == "greeting":
            return "greeting"

        return "direct_answer"

    return "rewrite"

def greeting_node(state: AgentState):
    return {
        "answer": "Hello! How can I assist you today?"
    }

def direct_answer_node(state: AgentState):
    user_query = state.get("user_query", "")
    owner_id = state["owner_id"]

    results = retrieve_memories(
        user_query=user_query,
        owner_id=owner_id,
        k=5
    )

    memories = []

    for result in results:
        memories.append(
            MemoryResponse(
                ownerId=result.metadata["ownerId"],
                type=result.metadata["type"],
                key=result.metadata["key"],
                value=result.metadata["value"],
                importance=result.metadata["importance"],
                createdAt=result.metadata["createdAt"],
                updatedAt=result.metadata["updatedAt"],
            )
        )

    response = direct_response_chain.invoke(
        {
            "user_query": user_query,
            "memories": memories
        }
    )

    return {
        "answer": response.content
    }

def rewrite_node(state: AgentState):
    user_query = state.get("user_query", "")
    conversation_history = state["conversation_history"]

    search_query = user_query  # Default to user query if no history is present

    if conversation_history:
        search_query = rewrite_query(
            query = user_query, 
            history = conversation_history
        )

    return {
        "search_query": search_query
    }

def extract_filters_node(state: AgentState):
    search_query = state.get("search_query", "")
    filters = extract_filters(search_query)


    return {
        "filters": filters
    }

def resolve_filters_node(state: AgentState):
    resolved_filters = resolve_filters(
        state["filters"], 
        state["owner_id"]
    )

    if state["collection_ids"]:
        resolved_filters.collection_ids = list(
            set(resolved_filters.collection_ids)
            | set(state["collection_ids"])
        )

    return {
        "resolved_filters": resolved_filters
    }

def planner_node(state: AgentState):
    plan = state["plan"]

    if plan is None:
        plan = create_plan(
            user_query=state["search_query"],
            feedback=state["feedback"],
            previous_plan=state["plan"],
            conversation_history=state["conversation_history"],
            image_data=state["image"],
            image_available=state["image"] is not None,
            web_enabled=state["web_enabled"]
        )

    return {
        "plan": plan
    }

async def executer_node(state: AgentState):
    context = await execute(
        plan=state["plan"],
        filters=state["resolved_filters"],
        owner_id=state["owner_id"],
        image=state.get("image")
    )
    return {
        "context": context
    }

def reflection_node(state: AgentState):
    reflection = reflect(
        user_query=state["search_query"],
        plan=state["plan"],
        context=state["context"]
    )

    updates = {
        "reflection": reflection
    }

    if not reflection.approved:
        updates["retry_count"] = state["retry_count"] + 1
        if reflection.action == "replan":
            updates["plan"] = None
            updates["feedback"] = f"""
                Previous Plan Failed

                Reason: {reflection.reason}
                Suggested Action: {reflection.action}
            """

    return updates

def route_after_reflection(state: AgentState):
    if state["reflection"].approved:
        return "synthesizer"

    if state["retry_count"] >= MAX_RETRIES:
        return "synthesizer"

    if state["reflection"].action == "replan":
        return "planner"

    if state["reflection"].action == "retry_tool":
        return "executer"

    return "synthesizer"

def synthesizer_node(state: AgentState):
    answer, sources = synthesize(
        user_query=state["search_query"],
        context=state["context"],
        history=state["conversation_history"],
        reflection=state["reflection"]
    )

    return {
        "answer": answer,
        "sources": sources
    }