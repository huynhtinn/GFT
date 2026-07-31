from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from app.graph.state import SupportState
from app.graph.nodes import (
    spam_duplicate_detector_node,
    intent_priority_classifier_node,
    slot_completeness_inspector_node,
    supervisor_node,
    query_optimizer_node,
    qdrant_rag_retrieval_node,
    reasoning_node,
    guardrails_router_node,
    hitl_briefing_generator_node
)

def should_continue_after_spam(state: SupportState) -> str:
    """Routing logic sau node Spam Check."""
    if state.get("is_spam", False):
        return "end"
    return "classify"

def should_continue_after_slot(state: SupportState) -> str:
    """Routing logic sau node Slot Check."""
    if state.get("status") == "CLARIFICATION_SENT":
        return "end"
    return "rag"

def should_continue_after_guardrails(state: SupportState) -> str:
    """Routing logic sau node Guardrails Router."""
    if state.get("status") == "ESCALATED_HUMAN":
        return "briefing"
    return "end"

def build_support_agent_graph():
    """Lắp ráp LangGraph State Machine cho Hệ thống Hỗ trợ Tự vận hành."""
    builder = StateGraph(SupportState)

    # Add Nodes
    builder.add_node("spam_check", spam_duplicate_detector_node)
    builder.add_node("classify", intent_priority_classifier_node)
    builder.add_node("slot_check", slot_completeness_inspector_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("query_optimize", query_optimizer_node)
    builder.add_node("rag_search", qdrant_rag_retrieval_node)
    builder.add_node("reasoning", reasoning_node)
    builder.add_node("guardrails", guardrails_router_node)
    builder.add_node("briefing", hitl_briefing_generator_node)

    # Set Entry Point
    builder.set_entry_point("spam_check")

    # Add Conditional Edges
    builder.add_conditional_edges(
        "spam_check",
        should_continue_after_spam,
        {
            "end": END,
            "classify": "classify"
        }
    )

    builder.add_edge("classify", "slot_check")

    builder.add_conditional_edges(
        "slot_check",
        should_continue_after_slot,
        {
            "end": END,
            "rag": "supervisor"
        }
    )

    # Wire supervisor, query optimizer, and reasoning layers
    builder.add_edge("supervisor", "query_optimize")
    builder.add_edge("query_optimize", "rag_search")
    builder.add_edge("rag_search", "reasoning")
    builder.add_edge("reasoning", "guardrails")

    builder.add_conditional_edges(
        "guardrails",
        should_continue_after_guardrails,
        {
            "end": END,
            "briefing": "briefing"
        }
    )

    builder.add_edge("briefing", END)

    # Checkpointer cho LangGraph State Persistence & HITL Interrupts
    checkpointer = MemorySaver()
    compiled_graph = builder.compile(checkpointer=checkpointer)

    return compiled_graph

# Global compiled LangGraph instance
support_agent_graph = build_support_agent_graph()
