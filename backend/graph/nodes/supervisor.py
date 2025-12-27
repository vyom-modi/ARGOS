import os
from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from backend.graph.state import AgentState

class RouteResponse(BaseModel):
    next: Literal["Explorer", "Auditor", "Execution", "Human", "FINISH"]

def supervisor_node(state: AgentState):
    llm = ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model="openai/gpt-oss-120b"
    )

    members = ["Explorer", "Auditor", "Execution", "Human"]
    
    system_prompt = (
        "You are a Site Reliability Engineering Supervisor (ARGOS) managing a swarm of agents: {members}.\n"
        "Your goal is to autonomously diagnose, fix, and verify issues.\n"
        "1. Explorer: Inspects the system, reads files, checking docker containers.\n"
        "2. Auditor: Runs security scans (bandit, safety) on proposed code.\n"
        "3. Execution: Runs tests in the E2B sandbox.\n"
        "4. Human: Requests approval for critical changes or deployment.\n\n"
        "Use the conversation history to decide who should act next.\n"
        "If a fix is proposed, perform a Security Audit first.\n"
        "If the audit passes, send it to Execution for testing.\n"
        "If tests pass, ask for Human approval.\n"
        "If the task is complete, respond with FINISH."
    )
    
    options = ["FINISH"] + members
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}",
            ),
        ]
    ).partial(options=str(options), members=", ".join(members))

    # Use structured output for type safety and to avoid parser issues
    structured_llm = llm.with_structured_output(RouteResponse)
    chain = prompt | structured_llm

    try:
        result = chain.invoke(state)
        # result is an instance of RouteResponse at this point
        next_step = result.next
    except Exception as e:
        print(f"Supervisor Error (likely missing API key or parsing fail): {e}")
        # Default to human intervention or finish on error
        next_step = "FINISH"

    return {"next": next_step}
