from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_reply(monkeypatch):
    monkeypatch.setattr(main, "run_agent", lambda text, session_id: "Hello!")

    response = client.post("/chat", json={"text": "Hi", "session_id": "s1"})

    assert response.status_code == 200
    assert response.json() == {"reply": "Hello!"}


def test_chat_rejects_empty_text():
    response = client.post("/chat", json={"text": ""})
    assert response.status_code == 422


def test_chat_returns_502_when_agent_fails(monkeypatch):
    def boom(text, session_id):
        raise RuntimeError("LLM down")

    monkeypatch.setattr(main, "run_agent", boom)

    response = client.post("/chat", json={"text": "Hi"})

    assert response.status_code == 502
