from langgraph.graph import StateGraph, START, END

from graph.state import AgentState
from graph.nodes import direct_answer_node, memory_node ,intent_node, route_after_intent, greeting_node, rewrite_node, extract_filters_node, resolve_filters_node, planner_node, executer_node, reflection_node, route_after_reflection, synthesizer_node

builder = StateGraph(AgentState)

# NODES
builder.add_node("memory", memory_node)
builder.add_node("intent", intent_node)
builder.add_node("greeting", greeting_node)
builder.add_node("direct_answer", direct_answer_node)
builder.add_node("rewrite", rewrite_node)
builder.add_node("extract_filters", extract_filters_node)
builder.add_node("resolve_filters", resolve_filters_node)
builder.add_node("planner", planner_node)
builder.add_node("executer", executer_node)
builder.add_node("reflection", reflection_node)
builder.add_node("synthesizer", synthesizer_node)


# EDGES
builder.add_edge(START, "memory")
builder.add_edge("memory", "intent")
builder.add_conditional_edges("intent", route_after_intent)

builder.add_edge("greeting", END)

builder.add_edge("rewrite", "extract_filters")
builder.add_edge("extract_filters", "resolve_filters")

builder.add_edge("resolve_filters", "planner")
builder.add_edge("planner", "executer")

builder.add_edge("executer", "reflection")

builder.add_conditional_edges("reflection", route_after_reflection)

builder.add_edge("synthesizer", END)

graph = builder.compile()