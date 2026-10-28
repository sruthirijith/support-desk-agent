import os
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from agent import run_agent

load_dotenv()

app = FastAPI(title="Support Desk Agent")

# Model name comes from .env so you can change it without touching code.
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-flash-latest"),
    temperature=0,
    timeout=30,
    max_retries=2,
)


class Message(BaseModel):
    text: str = Field(..., min_length=1, description="Customer message")


class Triage(BaseModel):
    """Structured result the LLM must return."""

    category: Literal["order", "refund", "general"]
    urgency: Literal["low", "medium", "high"]
    summary: str = Field(description="One-sentence summary of the issue")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a support triage assistant. Classify the customer's "
            "message by category and urgency, and summarise it in one sentence.",
        ),
        ("human", "{text}"),
    ]
)

# Prompt -> LLM that is forced to answer in the Triage shape
triage_chain = prompt | llm.with_structured_output(Triage)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/triage", response_model=Triage)
def triage(message: Message):
    try:
        return triage_chain.invoke({"text": message.text})
    except Exception as exc:  # LLM/network/quota errors
        raise HTTPException(status_code=502, detail=f"LLM call failed: {exc}")


class ChatReply(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatReply)
def chat(message: Message):
    try:
        return {"reply": run_agent(message.text)}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Agent failed: {exc}")