import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import InMemorySaver

from db import create_ticket, get_order
from rag import search_faq_text

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    temperature=0,
    timeout=60,
    max_retries=3,
)


@tool
def lookup_order(order_id: str) -> str:
    """Look up a customer order by its ID (format ORD-1234).
    Returns the order status, expected delivery date and total."""
    order = get_order(order_id)
    if order is None:
        return f"No order found with ID {order_id}."
    return json.dumps(order, default=str)  # default=str handles dates/decimals


@tool
def create_support_ticket(order_id: str, issue: str) -> str:
    """Create a support ticket for an existing order. Only call this after the
    customer has agreed to open a ticket. 'issue' is a short description."""
    if get_order(order_id) is None:
        return f"Cannot create a ticket: no order found with ID {order_id}."
    ticket_id = create_ticket(order_id, issue)
    return f"Ticket #{ticket_id} created for order {order_id.strip().upper()}."


@tool
def search_faq(question: str) -> str:
    """Search the company FAQ for policies: returns, refunds, shipping times,
    cancellations, delayed orders and support hours."""
    return search_faq_text(question)


SYSTEM_PROMPT = (
    "You are a polite customer support assistant. "
    "If the customer asks about an order, use the lookup_order tool with their "
    "order ID. If they haven't given an order ID, ask for it. "
    "For policy questions (returns, refunds, shipping, cancellations, support "
    "hours) use the search_faq tool and answer only from what it returns; if the "
    "FAQ doesn't cover it, say you don't know. "
    "If lookup_order shows the status is 'delayed', your reply MUST apologise "
    "for the delay and ask whether the customer would like a support ticket. "
    "Create it with create_support_ticket only after the customer agrees. "
    "Only state facts that come from the tools; never guess order details. "
    "You only help with orders, tickets and store policies. Greetings and "
    "thanks are fine. For anything unrelated, politely say you can only help "
    "with order and support questions. "
    "Keep replies short and friendly."
)

# The checkpointer saves each conversation's messages, keyed by thread_id
agent = create_agent(
    llm,
    tools=[lookup_order, create_support_ticket, search_faq],
    system_prompt=SYSTEM_PROMPT,
    checkpointer=InMemorySaver(),
)


def _to_text(content) -> str:
    """Gemini can return a string or a list of content blocks."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content
    )


def run_agent(user_message: str, session_id: str = "default") -> str:
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config,
    )
    return _to_text(result["messages"][-1].content)


if __name__ == "__main__":
    # Quick manual test: python agent.py
    print(run_agent("Where is my order ORD-1002?"))