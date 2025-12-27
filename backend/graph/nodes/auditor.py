import os
from langchain_groq import ChatGroq
from backend.graph.utils import create_agent_node
from backend.graph.tools import run_security_scan

def get_auditor_node():
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b")
    tools = [run_security_scan]
    system_message = "You are the Security Auditor. Run scans on code and report vulnerabilities."
    return create_agent_node(llm, tools, system_message)
