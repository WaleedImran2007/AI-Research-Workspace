from chains.planner_chain import planner_chain
from schemas.plan import Plan

def create_plan(
    user_query: str, 
    feedback: str = None, 
    previous_plan: Plan = None, 
    conversation_history: str = None,
    image_data: dict = None,
    image_available: bool = False,
    web_enabled: bool = False
) -> Plan:
    return planner_chain.invoke(
        {
            "user_query": user_query,
            "feedback": feedback,
            "previous_plan": previous_plan.json() if previous_plan else None,
            "conversation_history": conversation_history,
            "image_available": image_available,
            "image_data": image_data,
            "web_enabled": web_enabled
        }
    )