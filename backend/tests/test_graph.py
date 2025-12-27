import pytest
from langgraph.graph import StateGraph
from backend.main import graph

def test_graph_structure():
    """Verify the graph has all expected nodes."""
    assert "Supervisor" in graph.nodes
    assert "Explorer" in graph.nodes
    assert "Auditor" in graph.nodes
    assert "Execution" in graph.nodes
    assert "Human" in graph.nodes

def test_graph_compile():
    """Verify the graph compiles successfully."""
    runnable = graph
    assert runnable is not None
