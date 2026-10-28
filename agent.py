import json
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from db import get_order

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


SYSTEM_PROMPT = (
    "You are a polite customer support assistant. "
    "If the customer asks about an order, use the lookup_order tool with their "
    "order ID. If they haven't given an order ID, ask for it. "
    "Only state facts that come from the tool; never guess order details. "
    "Keep replies short and friendly."
)

agent = create_agent(llm, tools=[lookup_order], system_prompt=SYSTEM_PROMPT)


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