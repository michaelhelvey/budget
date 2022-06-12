from typing import NamedTuple, Optional, Union

import jwt
import bcrypt

from api import config
from api.domain import User


def create_jwt_for_user(user: User):
    payload = {"email": user.email}
    return jwt.encode(payload, config.AUTH_SECRET_KEY, algorithm="HS256")


def validate_token(token: str) -> Union[User, None]:
    try:
        payload = jwt.decode(token, config.AUTH_SECRET_KEY, algorithms=["HS256"])
        return User(**payload)
    except jwt.exceptions.DecodeError:
        return None


def hash_pw(passwd: str) -> str:
    return bcrypt.hashpw(passwd.encode(), config.AUTH_SECRET_KEY.encode())


# def check_password(email: str, plaintext_password: str) -> Union[User, None]:
#     user = get_user_with_email(email)
#     # compare password hashes
#     bcrypt.checkpw(plaintext_password.encode(), user.password_hash.encode())

#     return user
