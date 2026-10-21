from langgraph.graph import StateGraph, END
from app.services.agent.state import AgentState
from app.services.agent.nodes import (
    understand_question,
    decide_retrieval,
    rewrite_query,
    retrieve_context,
    check_context_quality,
    generate_answer
)

def should_retrieve(state: AgentState) -> str:
    """Conditional routing based on whether retrieval is needed."""
    if state["require_retrieval"]:
        return "rewrite_query"
    return "generate_answer"

def check_quality(state: AgentState) -> str:
    """Conditional routing based on context quality and attempt count."""
    if state["context_quality_score"] == "good":
        return "generate_answer"
    elif state["retrieval_attempts"] >= 3:
        # Give up and generate the best answer possible to avoid infinite loops
        print("Max retrieval attempts reached. Proceeding to generation.")
        return "generate_answer"
    else:
        # Context was poor, rewrite the query and try again
        return "rewrite_query"

# Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("understand_question", understand_question)
workflow.add_node("decide_retrieval", decide_retrieval)
workflow.add_node("rewrite_query", rewrite_query)
workflow.add_node("retrieve_context", retrieve_context)
workflow.add_node("check_context_quality", check_context_quality)
workflow.add_node("generate_answer", generate_answer)

# Set Entry Point
workflow.set_entry_point("understand_question")

# Add standard edges
workflow.add_edge("understand_question", "decide_retrieval")
workflow.add_edge("rewrite_query", "retrieve_context")
workflow.add_edge("retrieve_context", "check_context_quality")
workflow.add_edge("generate_answer", END)

# Add conditional edges
workflow.add_conditional_edges(
    "decide_retrieval",
    should_retrieve,
    {
        "rewrite_query": "rewrite_query",
        "generate_answer": "generate_answer"
    }
)

workflow.add_conditional_edges(
    "check_context_quality",
    check_quality,
    {
        "rewrite_query": "rewrite_query",
        "generate_answer": "generate_answer"
    }
)

# Compile the agent
agent_app = workflow.compile()
