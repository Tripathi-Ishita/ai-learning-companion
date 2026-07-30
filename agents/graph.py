"""agents/graph.py

Wires the nodes into a runnable graph.

Shape:
    START -> router -> one specialist -> (tools -> back to specialist)* -> END

The router is a WORKFLOW: a human-written rule picks the lane.
The tool loop is an AGENT: the model itself decides whether to search again.
"""

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from state import LearningState
from agents.tools import tools
from agents.nodes import route_intent, tutor_node, quiz_node, research_node


# ---------- routing functions (not nodes: they return a NAME, not a dict) ----------

def route_to_specialist(state: LearningState) -> str:
    """Which specialist handles this turn? Also used to get back after a tool run."""
    return state["intent"]


def should_continue(state: LearningState) -> str:
    """Did the specialist ask for a tool, and are we still allowed to run one?"""
    if state.get("step_count", 0) >= 6:
        return "end"
    # last message is always an AI message because the AI message only will tell tool call and only then should_continue executes.
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"

    return "end"


# ---------- build the graph ----------
# every piece of state flowing through you will have this shape
workflow = StateGraph(LearningState)
# when something points to the node called 'router', run the function route_intent
workflow.add_node("router", route_intent)
workflow.add_node("tutor", tutor_node)
workflow.add_node("quiz", quiz_node)
workflow.add_node("research", research_node)
workflow.add_node("tools", ToolNode(tools))

# every turn starts at the router
# every single time the graph runs, the very first thing \
# that happens is router. No conditions, no branching — 
# that's why it's add_edge, not add_conditional_edges
workflow.add_edge(START, "router")

# router -> the specialist named by state["intent"]
workflow.add_conditional_edges(
    "router",
    route_to_specialist,
    # match key->value(it's mapping "possible return values" to "actual node names,")
    {"tutor": "tutor", "quiz": "quiz", "research": "research"},
)

# each specialist -> tools, or finish
for specialist in ["tutor", "quiz", "research"]:
    workflow.add_conditional_edges(
        specialist,
        should_continue,
        {"tools": "tools", "end": END},
    )

# after the tool runs, go back to whoever asked for it
workflow.add_conditional_edges(
    "tools",
    route_to_specialist,
    {"tutor": "tutor", "quiz": "quiz", "research": "research"},
)

checkpointer = MemorySaver()

app = workflow.compile(checkpointer=checkpointer)