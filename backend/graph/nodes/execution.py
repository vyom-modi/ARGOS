import os
from langchain_groq import ChatGroq
from backend.graph.utils import create_agent_node
from backend.graph.tools import run_tests

def get_execution_node():
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b")
    tools = [run_tests]
    system_message = "You are the Execution Engine. Run tests and report results."
    return create_agent_node(llm, tools, system_message)
