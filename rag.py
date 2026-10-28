import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

_store = None  # built on first use, then reused


def _load_documents() -> list[Document]:
    """Split faq.md into one document per '## Title' section."""
    text = Path(__file__).with_name("faq.md").read_text(encoding="utf-8")
    docs = []
    for section in text.split("## ")[1:]:
        title, _, body = section.partition("\n")
        docs.append(
            Document(
                page_content=f"{title.strip()}: {body.strip()}",
                metadata={"title": title.strip()},
            )
        )
    return docs


def get_store() -> InMemoryVectorStore:
    global _store
    if _store is None:
        embeddings = GoogleGenerativeAIEmbeddings(model=os.environ["EMBED_MODEL"])
        _store = InMemoryVectorStore.from_documents(_load_documents(), embeddings)
    return _store


def search_faq_text(question: str, k: int = 2) -> str:
    """Return the k most relevant FAQ sections for the question."""
    results = get_store().similarity_search(question, k=k)
    return "\n\n".join(doc.page_content for doc in results)


if __name__ == "__main__":
    # Quick manual test: python rag.py
    print(search_faq_text("How long do refunds take?"))
