import rag


def test_faq_is_split_into_sections():
    docs = rag._load_documents()

    titles = [d.metadata["title"] for d in docs]
    assert len(docs) == 6
    assert "Refunds" in titles
    assert all(d.page_content.strip() for d in docs)
