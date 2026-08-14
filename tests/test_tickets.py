from tests.conftest import TICKET


def test_student_reports_a_ticket(ticket):
    assert ticket["status"] == "open" and ticket["assignee_id"] is None
    assert ticket["overdue"] is False


def test_only_students_report(client, people):
    r = client.post("/tickets", json=TICKET, headers=people["kiran"][1])
    assert r.status_code == 403


def test_bad_input_is_rejected(client, people):
    r = client.post("/tickets", json={**TICKET, "category": "magic"}, headers=people["asha"][1])
    assert r.status_code == 422


def test_students_cannot_see_each_others_tickets(client, people, ticket):
    url = f"/tickets/{ticket['id']}"
    assert client.get(url, headers=people["rohan"][1]).status_code == 404
    assert client.get("/tickets", headers=people["rohan"][1]).json() == []
    assert client.get(url, headers=people["vora"][1]).status_code == 200


def test_full_life_cycle(client, people, ticket):
    url = f"/tickets/{ticket['id']}"
    kiran, warden, asha = people["kiran"], people["vora"][1], people["asha"][1]
    r = client.post(f"{url}/assign", json={"technician_id": kiran[0].id}, headers=warden)
    assert r.json()["status"] == "assigned"
    assert [t["id"] for t in client.get("/tickets", headers=kiran[1]).json()] == [ticket["id"]]
    r = client.post(f"{url}/status", json={"status": "in_progress"}, headers=kiran[1])
    assert r.json()["status"] == "in_progress"
    r = client.post(f"{url}/status", json={"status": "resolved"}, headers=kiran[1])
    assert r.status_code == 400 and "note" in r.json()["detail"]
    r = client.post(
        f"{url}/status", json={"status": "resolved", "note": "Replaced capacitor"}, headers=kiran[1]
    )
    assert r.json()["status"] == "resolved" and r.json()["resolved_at"]
    r = client.post(f"{url}/status", json={"status": "closed"}, headers=asha)
    assert r.json()["status"] == "closed"
    detail = client.get(url, headers=asha).json()
    assert [c["body"] for c in detail["comments"]] == ["Replaced capacitor"]


def test_only_a_technician_can_be_assigned(client, people, ticket):
    r = client.post(
        f"/tickets/{ticket['id']}/assign",
        json={"technician_id": people["rohan"][0].id},
        headers=people["vora"][1],
    )
    assert r.status_code == 400 and "not a technician" in r.json()["detail"]


def test_student_may_cancel_only_while_open(client, people, ticket):
    url = f"/tickets/{ticket['id']}"
    client.post(
        f"{url}/assign", json={"technician_id": people["kiran"][0].id}, headers=people["vora"][1]
    )
    r = client.post(f"{url}/status", json={"status": "cancelled"}, headers=people["asha"][1])
    assert r.status_code == 400


def test_comments(client, people, ticket):
    r = client.post(
        f"/tickets/{ticket['id']}/comments",
        json={"body": "Still broken"},
        headers=people["asha"][1],
    )
    assert r.status_code == 201
    r = client.post(
        f"/tickets/{ticket['id']}/comments", json={"body": "Hi"}, headers=people["rohan"][1]
    )
    assert r.status_code == 404
