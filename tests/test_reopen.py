"""Reopening a fixed ticket (built by the software factory in Milestone 9)."""

from datetime import timedelta

import pytest

from app import services
from app.rules import RuleError, Status, utcnow


def resolve(client, people, ticket):
    url = f"/tickets/{ticket['id']}"
    client.post(
        f"{url}/assign", json={"technician_id": people["kiran"][0].id}, headers=people["vora"][1]
    )
    client.post(f"{url}/status", json={"status": "in_progress"}, headers=people["kiran"][1])
    r = client.post(
        f"{url}/status", json={"status": "resolved", "note": "Fixed"}, headers=people["kiran"][1]
    )
    assert r.json()["status"] == "resolved"
    return url


def test_reporter_reopens_within_seven_days(client, people, ticket):
    url = resolve(client, people, ticket)
    r = client.post(
        f"{url}/status",
        json={"status": "open", "note": "Fan stopped again"},
        headers=people["asha"][1],
    )
    body = r.json()
    assert r.status_code == 200 and body["status"] == "open"
    assert body["assignee_id"] is None and body["resolved_at"] is None
    assert body["due_at"] > ticket["due_at"]  # a fresh SLA


def test_reopen_after_seven_days_is_refused(client, db, people, ticket):
    resolve(client, people, ticket)
    t = services.get_visible(db, people["asha"][0], ticket["id"])
    with pytest.raises(RuleError, match="within 7 days"):
        services.change_status(
            db, people["asha"][0], t, Status.OPEN, now=utcnow() + timedelta(days=8)
        )


def test_only_the_reporter_reopens(client, people, ticket):
    url = resolve(client, people, ticket)
    r = client.post(f"{url}/status", json={"status": "open"}, headers=people["vora"][1])
    assert r.status_code == 400 and "Only the student" in r.json()["detail"]
