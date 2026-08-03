"""Graph builder: wire nodes, conditional edges, checkpointer."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver

from ..config import llm
from ..tools.flight import search_flights
from .nodes.plan_execution import plan_execute
from .nodes.response import response
from .nodes.trip_analysis import trip_analysis
from .state import TravelAgentState

tools = [
    search_flights,
]
tool_llm = llm.bind_tools(tools)


def build_enhanced_graph(checkpointer=None):
    """Build the production LangGraph workflow."""
    if checkpointer is None:
        checkpointer = InMemorySaver()

    workflow = StateGraph(TravelAgentState)

    workflow.add_node("trip_analysis", trip_analysis)
    workflow.add_node("plan_execution", plan_execute)
    workflow.add_node("response", response)

    workflow.set_entry_point("trip_analysis")
    # Edges
    workflow.add_edge("trip_analysis", "plan_execution")
    workflow.add_edge("plan_execution", "response")
    workflow.add_edge("response", END)

    print("Graph compiled successfully")
    return workflow.compile(checkpointer=checkpointer)