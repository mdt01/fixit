from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import rules, services
from app.db import get_db
from app.models import User
from app.rules import Category, Role, Status
from app.schemas import AssignIn, CommentIn, CommentOut, StatusIn, TicketDetail, TicketIn, TicketOut
from app.security import current_user, require

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=201)
def report_ticket(
    data: TicketIn, db: Session = Depends(get_db), user: User = Depends(require(Role.STUDENT))
) -> TicketOut:
    return services.to_out(services.create_ticket(db, user, data), rules.utcnow())


@router.get("", response_model=list[TicketOut])
def list_tickets(
    status: Status | None = None,
    category: Category | None = None,
    overdue: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> list[TicketOut]:
    now = rules.utcnow()
    tickets = services.visible_tickets(
        db, user, status=status, category=category, overdue_only=overdue, now=now
    )
    return [services.to_out(t, now) for t in tickets]


@router.get("/{ticket_id}", response_model=TicketDetail)
def ticket_detail(
    ticket_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)
) -> TicketOut:
    ticket = services.get_visible(db, user, ticket_id)
    return services.to_out(ticket, rules.utcnow(), TicketDetail)


@router.post("/{ticket_id}/assign", response_model=TicketOut)
def assign_ticket(
    ticket_id: int,
    data: AssignIn,
    db: Session = Depends(get_db),
    user: User = Depends(require(Role.WARDEN)),
) -> TicketOut:
    ticket = services.get_visible(db, user, ticket_id)
    return services.to_out(services.assign(db, user, ticket, data.technician_id), rules.utcnow())


@router.post("/{ticket_id}/status", response_model=TicketOut)
def change_status(
    ticket_id: int,
    data: StatusIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> TicketOut:
    ticket = services.get_visible(db, user, ticket_id)
    ticket = services.change_status(db, user, ticket, data.status, data.note)
    return services.to_out(ticket, rules.utcnow())


@router.post("/{ticket_id}/comments", response_model=CommentOut, status_code=201)
def comment(
    ticket_id: int,
    data: CommentIn,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> CommentOut:
    ticket = services.get_visible(db, user, ticket_id)
    return CommentOut.model_validate(services.add_comment(db, user, ticket, data.body))
