from datetime import datetime, timedelta

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.rules import (
    ACTIVE,
    TRANSITIONS,
    Category,
    Priority,
    Role,
    RuleError,
    Status,
    check_transition,
    due_at,
    is_overdue,
    sla_hours,
)

T0 = datetime(2026, 7, 1, 9, 0)


def test_sla_by_category_and_priority():
    assert sla_hours(Category.ELECTRICAL, Priority.NORMAL) == 24
    assert sla_hours(Category.ELECTRICAL, Priority.URGENT) == 6
    assert sla_hours(Category.CLEANING, Priority.URGENT) == 4  # never below 4 hours
    assert due_at(T0, Category.INTERNET, Priority.NORMAL) == T0 + timedelta(hours=48)


@given(st.sampled_from(list(Category)))
def test_urgent_is_never_slower_than_normal(category):
    assert sla_hours(category, Priority.URGENT) <= sla_hours(category, Priority.NORMAL)


@given(st.sampled_from(list(Status)), st.integers(min_value=-1000, max_value=1000))
def test_only_active_tickets_can_be_overdue(status, minutes):
    now = T0 + timedelta(minutes=minutes)
    assert is_overdue(status, T0, now) == (status in ACTIVE and minutes > 0)


def test_warden_assigns_and_technician_works():
    check_transition(
        role=Role.WARDEN,
        current=Status.OPEN,
        new=Status.ASSIGNED,
        is_reporter=False,
        is_assignee=False,
    )
    check_transition(
        role=Role.TECHNICIAN,
        current=Status.ASSIGNED,
        new=Status.IN_PROGRESS,
        is_reporter=False,
        is_assignee=True,
    )


@pytest.mark.parametrize(
    "role, current, new, reporter, assignee",
    [
        (Role.STUDENT, Status.OPEN, Status.ASSIGNED, True, False),  # students cannot assign
        (Role.TECHNICIAN, Status.ASSIGNED, Status.IN_PROGRESS, False, False),  # not theirs
        (Role.WARDEN, Status.IN_PROGRESS, Status.RESOLVED, False, False),  # only the technician
        (Role.STUDENT, Status.ASSIGNED, Status.CANCELLED, True, False),  # too late to cancel
        (Role.WARDEN, Status.CANCELLED, Status.OPEN, False, False),  # cancelled is final
    ],
)
def test_forbidden_moves(role, current, new, reporter, assignee):
    with pytest.raises(RuleError):
        check_transition(
            role=role, current=current, new=new, is_reporter=reporter, is_assignee=assignee
        )


@given(st.lists(st.sampled_from(list(Status)), max_size=12))
def test_random_walks_stay_on_the_graph(steps):
    """Whatever anyone tries, a ticket only ever moves along TRANSITIONS."""
    current, resolved = Status.OPEN, None
    for new in steps:
        for role in Role:
            try:
                check_transition(
                    role=role,
                    current=current,
                    new=new,
                    is_reporter=True,
                    is_assignee=True,
                    resolved_at=resolved,
                    now=T0,
                )
            except RuleError:
                continue
            assert new in TRANSITIONS[current]
            current, resolved = new, (T0 if new == Status.RESOLVED else resolved)
            break


def test_reopen_window():
    kw = {
        "role": Role.STUDENT,
        "current": Status.RESOLVED,
        "new": Status.OPEN,
        "is_assignee": False,
        "resolved_at": T0,
    }
    check_transition(is_reporter=True, now=T0 + timedelta(days=7), **kw)
    with pytest.raises(RuleError, match="within 7 days"):
        check_transition(is_reporter=True, now=T0 + timedelta(days=7, seconds=1), **kw)
    with pytest.raises(RuleError, match="Only the student"):
        check_transition(is_reporter=False, now=T0 + timedelta(days=1), **kw)
