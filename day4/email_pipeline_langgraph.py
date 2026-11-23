# email_pipeline_langgraph.py — LangGraph version (overkill here)
import config

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict

class EmailState(TypedDict):
    email_body: str
    intent: str
    draft: str

llm = ChatOpenAI(model="gpt-5.4-mini")

def classify_node(state: EmailState) -> dict:
    """Node that classifies the email's intent."""
    response = llm.invoke(
        f"Classify this support email intent. "
        f"Return exactly one of: billing, technical, feature_request, other.\n\n"
        f"{state['email_body']}"
    )
    return {"intent": response.content.strip()}

def draft_node(state: EmailState) -> dict:
    """Node that drafts a reply based on the classified intent."""
    response = llm.invoke(
        f"Draft a professional response to this {state['intent']} support email. "
        f"Be concise and helpful.\n\n{state['email_body']}"
    )
    return {"draft": response.content}

# Build the graph
graph = StateGraph(EmailState)
graph.add_node("classify", classify_node)
graph.add_node("draft", draft_node)
graph.set_entry_point("classify")
graph.add_edge("classify", "draft")
graph.add_edge("draft", END)

# Compilation (this step alone adds latency and an unnecessary dependency)
email_workflow = graph.compile()

# Usage: result = email_workflow.invoke({"email_body": "..."})
