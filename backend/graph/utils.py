from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from backend.graph.state import AgentState

def create_agent_node(llm, tools, system_message: str):
    """Create a node that acts as an agent."""
    
    # Simple tool binding
    llm_with_tools = llm.bind_tools(tools)
    
    def agent_node(state: AgentState):
        messages = state["messages"]
        # If the last message is from this agent, we might want to stop or continue
        result = llm_with_tools.invoke([("system", system_message)] + messages)
        return {"messages": [result]}
        
    return agent_node
