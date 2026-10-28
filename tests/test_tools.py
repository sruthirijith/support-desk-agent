import json

import agent


def test_lookup_order_found(monkeypatch):
    fake = {"order_id": "ORD-1002", "status": "delayed", "total": 2999.5}
    monkeypatch.setattr(agent, "get_order", lambda order_id: fake)

    result = agent.lookup_order.invoke({"order_id": "ORD-1002"})

    assert json.loads(result)["status"] == "delayed"


def test_lookup_order_not_found(monkeypatch):
    monkeypatch.setattr(agent, "get_order", lambda order_id: None)

    result = agent.lookup_order.invoke({"order_id": "ORD-9999"})

    assert "No order found" in result


def test_ticket_refused_for_unknown_order(monkeypatch):
    monkeypatch.setattr(agent, "get_order", lambda order_id: None)
    called = []
    monkeypatch.setattr(agent, "create_ticket", lambda *a: called.append(a))

    result = agent.create_support_ticket.invoke(
        {"order_id": "ORD-9999", "issue": "Not received"}
    )

    assert "Cannot create a ticket" in result
    assert called == []  # nothing was saved


def test_ticket_created_for_known_order(monkeypatch):
    monkeypatch.setattr(agent, "get_order", lambda order_id: {"order_id": "ORD-1002"})
    monkeypatch.setattr(agent, "create_ticket", lambda order_id, issue: 7)

    result = agent.create_support_ticket.invoke(
        {"order_id": "ord-1002", "issue": "Order delayed"}
    )

    assert "Ticket #7" in result
    assert "ORD-1002" in result
