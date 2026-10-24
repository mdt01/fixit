"""Ticket operations: apply the rules in app/rules.py to the database."""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import rules
from app.models import Comment, Ticket, User
from app.rules import Category, Role, RuleError, Status
from app.schemas import TicketIn, TicketOut, WorkloadRow

log = logging.getLogger(__name__)


class NotFound(LookupError):
    """The ticket does not exist, or this user may not see it (we do not say which)."""


def to_out(ticket: Ticket, now: datetime, schema: type[TicketOut] = TicketOut) -> TicketOut:
    out = schema.model_validate(ticket)
    out.overdue = rules.is_overdue(ticket.status, ticket.due_at, now)
    return out


def create_ticket(
    db: Session, reporter: User, data: TicketIn, now: datetime | None = None
) -> Ticket:
    now = now or rules.utcnow()
    ticket = Ticket(
        **data.model_dump(),
        reporter_id=reporter.id,
        created_at=now,
        due_at=rules.due_at(now, data.category, data.priority),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def visible_tickets(
    db: Session,
    user: User,
    *,
    status: Status | None = None,
    category: Category | None = None,
    overdue_only: bool = False,
    now: datetime | None = None,
) -> list[Ticket]:
    """Students see their own tickets, technicians their assigned ones, wardens all."""
    now = now or rules.utcnow()
    query = select(Ticket).order_by(Ticket.due_at)
    if user.role == Role.STUDENT:
        query = query.where(Ticket.reporter_id == user.id)
    elif user.role == Role.TECHNICIAN:
        query = query.where(Ticket.assignee_id == user.id)
    if status:
        query = query.where(Ticket.status == status)
    if category:
        query = query.where(Ticket.category == category)
    tickets = list(db.scalars(query))
    if overdue_only:
        tickets = [t for t in tickets if rules.is_overdue(t.status, t.due_at, now)]
    return tickets


def get_visible(db: Session, user: User, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or not (
        user.role == Role.WARDEN or ticket.reporter_id == user.id or ticket.assignee_id == user.id
    ):
        raise NotFound(f"Ticket {ticket_id} not found.")
    return ticket


def assign(db: Session, warden: User, ticket: Ticket, technician_id: int) -> Ticket:
    technician = db.get(User, technician_id)
    if technician is None or technician.role != Role.TECHNICIAN:
        raise RuleError(f"User {technician_id} is not a technician.")
    rules.check_transition(
        role=warden.role,
        current=ticket.status,
        new=Status.ASSIGNED,
        is_reporter=False,
        is_assignee=False,
    )
    ticket.assignee_id = technician.id
    ticket.status = Status.ASSIGNED
    log.info("ticket %s assigned to technician %s by %s", ticket.id, technician.id, warden.id)
    db.commit()
    return ticket


def change_status(
    db: Session,
    user: User,
    ticket: Ticket,
    new: Status,
    note: str | None = None,
    now: datetime | None = None,
) -> Ticket:
    now = now or rules.utcnow()
    rules.check_transition(
        role=user.role,
        current=ticket.status,
        new=new,
        is_reporter=ticket.reporter_id == user.id,
        is_assignee=ticket.assignee_id == user.id,
    )
    if new == Status.RESOLVED and not note:
        raise RuleError("Add a note that says what was fixed.")
    if new == Status.OPEN:  # un-assigned
        ticket.assignee_id = None
    if new == Status.RESOLVED:
        ticket.resolved_at = now
    log.info("ticket %s: %s -> %s by user %s", ticket.id, ticket.status, new, user.id)
    ticket.status = new
    if note:
        db.add(Comment(ticket_id=ticket.id, author_id=user.id, body=note, created_at=now))
    db.commit()
    db.refresh(ticket)
    return ticket


def add_comment(db: Session, user: User, ticket: Ticket, body: str) -> Comment:
    comment = Comment(ticket_id=ticket.id, author_id=user.id, body=body)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def workload(db: Session, now: datetime | None = None) -> list[WorkloadRow]:
    now = now or rules.utcnow()
    rows = []
    for tech in db.scalars(select(User).where(User.role == Role.TECHNICIAN).order_by(User.id)):
        assigned = db.scalars(select(Ticket).where(Ticket.assignee_id == tech.id))
        active = [t for t in assigned if t.status in rules.ACTIVE]
        overdue = sum(rules.is_overdue(t.status, t.due_at, now) for t in active)
        rows.append(
            WorkloadRow(technician_id=tech.id, name=tech.name, active=len(active), overdue=overdue)
        )
    return rows
