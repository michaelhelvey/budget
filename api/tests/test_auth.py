from api.auth import create_jwt_for_user, validate_token
from api.domain import User


def test_can_create_and_validate_jwt():
    user = User(email="michael@example.com")
    token = create_jwt_for_user(user)

    assert validate_token(token).email == user.email


def test_given_invalid_token_validate_returns_none():
    assert validate_token("blah") is None
