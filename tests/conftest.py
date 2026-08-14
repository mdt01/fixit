import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app
from app.models import User
from app.rules import Role
from app.security import hash_password

PASSWORD = "test-pass-123"


@pytest.fixture()
def db():
    """A fresh in-memory database for every test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, autoflush=False)()
    yield session
    session.close()


@pytest.fixture()
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def make_user(db):
    def make(name: str, role: Role) -> User:
        user = User(
            name=name,
            email=f"{name.lower()}@test.example",
            role=role,
            password_hash=hash_password(PASSWORD),
        )
        db.add(user)
        db.commit()
        return user

    return make


@pytest.fixture()
def login(client):
    """Return request headers for a logged-in user."""

    def do(user: User) -> dict[str, str]:
        r = client.post("/auth/login", json={"email": user.email, "password": PASSWORD})
        assert r.status_code == 200, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}

    return do


@pytest.fixture()
def people(make_user, login):
    """Two students, a technician and a warden, already logged in."""
    users = {
        "asha": make_user("Asha", Role.STUDENT),
        "rohan": make_user("Rohan", Role.STUDENT),
        "kiran": make_user("Kiran", Role.TECHNICIAN),
        "vora": make_user("Vora", Role.WARDEN),
    }
    return {name: (user, login(user)) for name, user in users.items()}


TICKET = {
    "title": "Fan not working",
    "description": "Ceiling fan stops after a minute.",
    "category": "electrical",
    "location": "Hostel A, room 204",
}


@pytest.fixture()
def ticket(client, people):
    r = client.post("/tickets", json=TICKET, headers=people["asha"][1])
    assert r.status_code == 201, r.text
    return r.json()
