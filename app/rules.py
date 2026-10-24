"""FixIt business rules: pure functions, no database and no web framework.

Everything here can be tested in milliseconds, which makes it the safest place for an
agent (or a person) to change behaviour.
"""

from datetime import UTC, datetime, timedelta
from enum import StrEnum


class Role(StrEnum):
    STUDENT = "student"
    TECHNICIAN = "technician"
    WARDEN = "warden"


class Category(StrEnum):
    ELECTRICAL = "electrical"
    PLUMBING = "plumbing"
    INTERNET = "internet"
    FURNITURE = "furniture"
    CLEANING = "cleaning"
    OTHER = "other"


class Priority(StrEnum):
    NORMAL = "normal"
    URGENT = "urgent"


class Status(StrEnum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"


ACTIVE = {Status.OPEN, Status.ASSIGNED, Status.IN_PROGRESS}

# Hours allowed to resolve a ticket (the service-level agreement, SLA).
SLA_HOURS = {
    Category.ELECTRICAL: 24,
    Category.PLUMBING: 24,
    Category.INTERNET: 48,
    Category.FURNITURE: 72,
    Category.CLEANING: 12,
    Category.OTHER: 72,
}
URGENT_MIN_HOURS = 4
REOPEN_DAYS = 7

# The ticket life cycle: which status may follow which.
TRANSITIONS: dict[Status, set[Status]] = {
    Status.OPEN: {Status.ASSIGNED, Status.CANCELLED},
    Status.ASSIGNED: {Status.IN_PROGRESS, Status.OPEN, Status.CANCELLED},
    Status.IN_PROGRESS: {Status.RESOLVED},
    Status.RESOLVED: {Status.CLOSED, Status.OPEN},
    Status.CLOSED: {Status.OPEN},
    Status.CANCELLED: set(),
}


class RuleError(ValueError):
    """A request that breaks a business rule. The message is shown to the user."""


def utcnow() -> datetime:
    """The current time in UTC, without tzinfo (how SQLite stores it)."""
    return datetime.now(UTC).replace(tzinfo=None)


def sla_hours(category: Category, priority: Priority) -> int:
    hours = SLA_HOURS[category]
    if priority == Priority.URGENT:
        hours = max(URGENT_MIN_HOURS, hours // 4)
    return hours


def due_at(created_at: datetime, category: Category, priority: Priority) -> datetime:
    return created_at + timedelta(hours=sla_hours(category, priority))


def is_overdue(status: Status, due: datetime, now: datetime) -> bool:
    return status in ACTIVE and now > due


def check_transition(
    *,
    role: Role,
    current: Status,
    new: Status,
    is_reporter: bool,
    is_assignee: bool,
    resolved_at: datetime | None = None,
    now: datetime | None = None,
) -> None:
    """Raise RuleError unless this user may move a ticket from `current` to `new`."""
    if new not in TRANSITIONS[current]:
        raise RuleError(f"A ticket cannot go from '{current}' to '{new}'.")
    if current in {Status.RESOLVED, Status.CLOSED} and new == Status.OPEN:
        if not is_reporter:
            raise RuleError("Only the student who reported a ticket can reopen it.")
        now = now or utcnow()
        if resolved_at is None or now - resolved_at > timedelta(days=REOPEN_DAYS):
            raise RuleError(
                f"Tickets can be reopened only within {REOPEN_DAYS} days "
                "of being resolved. Please report a new ticket."
            )
        return
    allowed = {
        Status.ASSIGNED: role == Role.WARDEN,
        Status.OPEN: role == Role.WARDEN,  # un-assign
        Status.CANCELLED: role == Role.WARDEN or (is_reporter and current == Status.OPEN),
        Status.IN_PROGRESS: role == Role.TECHNICIAN and is_assignee,
        Status.RESOLVED: role == Role.TECHNICIAN and is_assignee,
        Status.CLOSED: role == Role.WARDEN or is_reporter,
    }[new]
    if not allowed:
        raise RuleError(f"A {role} cannot move this ticket to '{new}'.")
