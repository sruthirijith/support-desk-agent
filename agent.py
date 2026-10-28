import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from db import create_ticket, get_order

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    temperature=0,
    timeout=30,
    max_retries=2,
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


SYSTEM_PROMPT = (
    "You are a polite customer support assistant. "
    "If the customer asks about an order, use the lookup_order tool with their "
    "order ID. If they haven't given an order ID, ask for it. "
    "If an order is delayed, apologise and offer to create a support ticket; "
    "create it with create_support_ticket only after the customer agrees. "
    "Only state facts that come from the tools; never guess order details. "
    "Keep replies short and friendly."
)

agent = create_agent(llm, tools=[lookup_order, create_support_ticket], system_prompt=SYSTEM_PROMPT)


def _to_text(content) -> str:
    """Gemini can return a string or a list of content blocks."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block)
        for block in content
    )


def run_agent(user_message: str) -> str:
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    return _to_text(result["messages"][-1].content)


if __name__ == "__main__":
    # Quick manual test: python agent.py
    print(run_agent("Where is my order ORD-1002?"))
