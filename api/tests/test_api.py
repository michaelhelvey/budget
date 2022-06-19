from api.auth import AuthProvider
from api.db import get_db_instance
from api.main import app

from fastapi.testclient import TestClient

from .utils import util_create_user

client = TestClient(app)


def test_login():
    user = util_create_user(name="Foo", email="foo@bar.com", password="1234")
    db = get_db_instance()
    auth = AuthProvider(db)

    response = client.post(
        "/accounts/login", json={"email": "foo@bar.com", "password": "1234"}
    )
    token = response.cookies.get("auth_token")

    assert auth.validate_token(token).email == user.email


def test_accounts_me():
    user = util_create_user(name="Bar", email="foo@bar.com", password="1234")
    db = get_db_instance()
    auth = AuthProvider(db)
    token = auth.create_jwt_for_user(user)

    response = client.get("/accounts/me", cookies={"auth_token": token})

    response_json = response.json()
    user_json = user.dict()

    for key in ["name", "email"]:
        assert user_json[key] == response_json["user"][key]
