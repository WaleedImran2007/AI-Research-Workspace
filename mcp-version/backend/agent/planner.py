from chains.planner_chain import planner_chain
from schemas.plan import Plan

def create_plan(user_query: str, feedback: str = None, previous_plan: Plan = None) -> Plan:
    return planner_chain.invoke(
        {
            "user_query": user_query,
            "feedback": feedback,
            "previous_plan": previous_plan.json() if previous_plan else None
        }
    )