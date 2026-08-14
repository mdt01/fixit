from datetime import timedelta

from app.models import User
from app.rules import Role, utcnow
from tests.conftest import PASSWORD


def test_login_and_me(client, make_user, login):
    user = make_user("Asha", Role.STUDENT)
    me = client.get("/me", headers=login(user)).json()
    assert me["email"] == "asha@test.example" and me["role"] == "student"


def test_wrong_password_and_unknown_email_look_the_same(client, make_user):
    make_user("Asha", Role.STUDENT)
    wrong = client.post("/auth/login", json={"email": "asha@test.example", "password": "x"})
    unknown = client.post(
        "/auth/login", json={"email": "nobody@test.example", "password": PASSWORD}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_requests_need_a_valid_token(client):
    assert client.get("/tickets").status_code == 401
    assert client.get("/tickets", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_expired_token_is_rejected(client, db, make_user, login):
    user = make_user("Asha", Role.STUDENT)
    headers = login(user)
    user.token_expires = utcnow() - timedelta(minutes=1)
    db.commit()
    assert client.get("/me", headers=headers).status_code == 401


def test_secrets_are_stored_only_as_hashes(db, make_user, login):
    user = make_user("Asha", Role.STUDENT)
    token = login(user)["Authorization"].split()[1]
    stored = db.get(User, user.id)
    assert PASSWORD not in stored.password_hash
    assert stored.token_hash != token and len(stored.token_hash) == 64
