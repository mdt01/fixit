from datetime import timedelta

from app import services
from app.rules import Category, Status, utcnow
from app.schemas import TicketIn


def report(db, user, hours_ago, category=Category.CLEANING):
    data = TicketIn(
        title="Room not cleaned",
        description="Bins not emptied for days.",
        category=category,
        location="Hostel B, 3rd floor",
    )
    return services.create_ticket(db, user, data, now=utcnow() - timedelta(hours=hours_ago))


def test_overdue_report_lists_late_active_tickets_only(client, db, people):
    asha = people["asha"][0]
    late = report(db, asha, hours_ago=20)  # cleaning SLA is 12 hours
    report(db, asha, hours_ago=1)  # still on time
    done = report(db, asha, hours_ago=30)
    done.status = Status.CANCELLED
    db.commit()
    rows = client.get("/reports/overdue", headers=people["vora"][1]).json()
    assert [r["id"] for r in rows] == [late.id] and rows[0]["overdue"] is True


def test_reports_are_for_wardens_only(client, people):
    assert client.get("/reports/overdue", headers=people["asha"][1]).status_code == 403
    assert client.get("/reports/workload", headers=people["kiran"][1]).status_code == 403


def test_workload(client, db, people):
    kiran = people["kiran"][0]
    for ticket in (report(db, people["asha"][0], 20), report(db, people["asha"][0], 1)):
        services.assign(db, people["vora"][0], ticket, kiran.id)
    rows = client.get("/reports/workload", headers=people["vora"][1]).json()
    assert rows == [{"technician_id": kiran.id, "name": "Kiran", "active": 2, "overdue": 1}]
