import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app import rules, services
from app.db import get_db
from app.models import User
from app.rules import Role
from app.schemas import TicketOut, WorkloadRow
from app.security import require

router = APIRouter(prefix="/reports", tags=["reports"])
warden_only = require(Role.WARDEN)


@router.get("/overdue", response_model=list[TicketOut])
def overdue(db: Session = Depends(get_db), user: User = Depends(warden_only)) -> list[TicketOut]:
    """Overdue tickets, the most overdue first."""
    now = rules.utcnow()
    return [
        services.to_out(t, now)
        for t in services.visible_tickets(db, user, overdue_only=True, now=now)
    ]


@router.get("/overdue.csv", response_class=PlainTextResponse)
def overdue_csv(db: Session = Depends(get_db), user: User = Depends(warden_only)) -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["id", "title", "category", "location", "status", "due_at"])
    for t in services.visible_tickets(db, user, overdue_only=True):
        writer.writerow(
            [
                t.id,
                t.title,
                t.category,
                t.location,
                t.status,
                t.due_at.isoformat(timespec="minutes"),
            ]
        )
    return out.getvalue()


@router.get("/workload", response_model=list[WorkloadRow])
def workload(db: Session = Depends(get_db), user: User = Depends(warden_only)) -> list[dict]:
    return services.workload(db)
