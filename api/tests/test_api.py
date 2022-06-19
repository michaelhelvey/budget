import json
import os

import pytest
from api.auth import AuthProvider
from api.db import (
    get_db_instance,
    get_user_with_email,
    save_state_to_file,
    _delete_db_singleton,
)
from api.main import app
from api.domain import ApplicationState
from fastapi import status
from fastapi.testclient import TestClient

from .utils import reset_db, util_create_user

client = TestClient(app)


@pytest.fixture
def auth_token():
    user = util_create_user(name="Bar", email="foo@bar.com", password="1234")
    db = get_db_instance()
    auth = AuthProvider(db)
    token = auth.create_jwt_for_user(user)

    return user, token


def test_login():
    user = util_create_user(name="Foo", email="foo@bar.com", password="1234")
    db = get_db_instance()
    auth = AuthProvider(db)

    response = client.post(
        "/accounts/login", json={"email": "foo@bar.com", "password": "1234"}
    )
    token = response.cookies.get("auth_token")

    assert auth.validate_token(token).email == user.email


def test_accounts_create():
    body = {"name": "foo", "email": "bar@example.com", "password": 1234}
    response = client.post("/accounts/create", json=body)
    json_body = response.json()
    assert json_body["name"] == "foo"
    assert json_body["email"] == "bar@example.com"

    db = get_db_instance()
    db_user = get_user_with_email(db, "bar@example.com")
    assert db_user.name == "foo"


def test_accounts_me(auth_token):
    user, token = auth_token
    response = client.get("/accounts/me", cookies={"auth_token": token})

    response_json = response.json()
    user_json = user.dict()

    for key in ["name", "email"]:
        assert user_json[key] == response_json["user"][key]


def test_user_required_no_user_token():
    client.cookies.clear()
    response = client.get("/accounts/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_add_transaction(auth_token):
    user, token = auth_token
    body = {
        "category": "Grocery",
        "amount": 100,
        "title": "Hi",
        "notes": "foo bar quux",
    }
    response = client.post("/transactions", cookies={"auth_token": token}, json=body)

    assert response.status_code == status.HTTP_201_CREATED

    db = get_db_instance()
    first_db_transaction = db.get_current_state().transactions[0]
    for key in body.keys():
        assert first_db_transaction.dict()[key] == body[key]


def test_get_state(auth_token):
    user, token = auth_token
    response = client.get("/_internal/state", cookies={"auth_token": token})

    db = get_db_instance()
    # smoke test
    assert response.json()["users"] == db.dict()["users"]


def test_get_summary(auth_token):
    test_dir = os.path.dirname(__file__)
    reset_db()
    db = get_db_instance()
    with open(os.path.join(test_dir, "fixtures", "test_db_state.json")) as db_file:
        db = ApplicationState(**json.loads(db_file.read()))
        save_state_to_file(db)
        _delete_db_singleton()
        with open(
            os.path.join(test_dir, "fixtures", "report_snapshot.json")
        ) as response_file:
            user, token = auth_token
            response = client.get("/months/current", cookies={"auth_token": token})


            assert response.status_code == status.HTTP_200_OK
            expected_response = json.loads(response_file.read())
            assert response.json() == expected_response
