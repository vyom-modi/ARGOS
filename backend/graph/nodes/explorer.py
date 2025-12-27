import os
from langchain_groq import ChatGroq
from backend.graph.utils import create_agent_node
from backend.graph.tools import list_files, read_file, list_docker_containers

def get_explorer_node():
    llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model="openai/gpt-oss-120b")
    tools = [list_files, read_file, list_docker_containers]
    system_message = "You are the Explorer agent. Your job is to navigate the file system and understand the codebase."
    return create_agent_node(llm, tools, system_message)
