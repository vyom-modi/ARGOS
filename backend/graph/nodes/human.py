from backend.graph.state import AgentState

def human_node(state: AgentState):
    """Node that represents a human approval step."""
    # In a real system, this might trigger a notification or wait for an external event.
    # For LangGraph, we update the state to indicate we are waiting.
    return {"approval_status": "PENDING", "messages": [{"role": "assistant", "content": "Waiting for human approval..."}]}
