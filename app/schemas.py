from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.rules import Category, Priority, Role, Status


class LoginIn(BaseModel):
    email: str
    password: str


class TokenOut(BaseModel):
    token: str
    name: str
    role: Role


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    role: Role


class TicketIn(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    category: Category
    location: str = Field(min_length=2, max_length=120)
    priority: Priority = Priority.NORMAL


class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    author_id: int
    body: str
    created_at: datetime


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    category: Category
    priority: Priority
    location: str
    status: Status
    reporter_id: int
    assignee_id: int | None
    created_at: datetime
    due_at: datetime
    resolved_at: datetime | None
    overdue: bool = False


class TicketDetail(TicketOut):
    comments: list[CommentOut] = []


class AssignIn(BaseModel):
    technician_id: int


class StatusIn(BaseModel):
    status: Status
    note: str | None = Field(default=None, max_length=1000)


class WorkloadRow(BaseModel):
    technician_id: int
    name: str
    active: int
    overdue: int
