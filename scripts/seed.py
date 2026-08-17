"""Load demo users and tickets:  python -m scripts.seed

Demo password for every account: FIXIT_DEMO_PASSWORD (default 'demo-pass-2026').
Never reuse it for anything real.
"""

import os
from datetime import timedelta

from app.db import Base, SessionLocal, engine
from app.models import Ticket, User
from app.rules import Category, Priority, Role, Status, due_at, utcnow
from app.security import hash_password

PASSWORD = os.getenv("FIXIT_DEMO_PASSWORD", "demo-pass-2026")
USERS = [
    ("Asha Patel", "asha@campus.example", Role.STUDENT),
    ("Rohan Mehta", "rohan@campus.example", Role.STUDENT),
    ("Kiran Shah", "kiran@campus.example", Role.TECHNICIAN),
    ("Meena Iyer", "meena@campus.example", Role.TECHNICIAN),
    ("Dr. Vora", "warden@campus.example", Role.WARDEN),
]


def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    users = [
        User(name=n, email=e, role=r, password_hash=hash_password(PASSWORD)) for n, e, r in USERS
    ]
    db.add_all(users)
    db.flush()
    asha, rohan, kiran = users[0], users[1], users[2]
    now = utcnow()
    samples = [
        (
            asha,
            "Ceiling fan not working",
            "Fan in room stops after a minute.",
            Category.ELECTRICAL,
            Priority.NORMAL,
            "Hostel A, room 204",
            30,
        ),
        (
            asha,
            "Wi-Fi drops every evening",
            "No internet from 8 pm to 11 pm daily.",
            Category.INTERNET,
            Priority.NORMAL,
            "Hostel A, 2nd floor",
            10,
        ),
        (
            rohan,
            "Water leaking from tap",
            "Bathroom tap leaks all night.",
            Category.PLUMBING,
            Priority.URGENT,
            "Hostel B, room 112",
            2,
        ),
    ]
    tickets = []
    for reporter, title, text, category, priority, where, hours_ago in samples:
        created = now - timedelta(hours=hours_ago)
        tickets.append(
            Ticket(
                title=title,
                description=text,
                category=category,
                priority=priority,
                location=where,
                reporter_id=reporter.id,
                created_at=created,
                due_at=due_at(created, category, priority),
            )
        )
    tickets[0].assignee_id, tickets[0].status = kiran.id, Status.ASSIGNED
    db.add_all(tickets)
    db.commit()
    print(f"Seeded {len(USERS)} users and {len(samples)} tickets. Password: {PASSWORD}")


if __name__ == "__main__":
    main()
