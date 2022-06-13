from types import SimpleNamespace
from unittest.mock import patch

import bcrypt
from api.auth import AuthProvider
from api.domain import User


def test_can_create_and_validate_jwt():
    auth = AuthProvider(None)
    user = User(email="michael@example.com")
    token = auth.create_jwt_for_user(user)

    assert auth.validate_token(token).email == user.email


def test_given_invalid_token_validate_returns_none():
    auth = AuthProvider(None)
    assert auth.validate_token("blah") is None


def test_given_user_in_db_can_sign_in_with_email_and_password():
    passwd_hash = bcrypt.hashpw("asdf".encode(), bcrypt.gensalt())
    user = User(email="eyore@example.com", password_hash=passwd_hash)
    auth = AuthProvider(db=SimpleNamespace(users=[user]))

    user = auth.check_password("eyore@example.com", "1234")
    assert user == user
