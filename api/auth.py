from datetime import timedelta, datetime
from typing import Union

import jwt
import bcrypt

from api import config
from api.domain import User
from api.db import get_user_with_email
from api.domain import ApplicationState

JWT_EXP = timedelta(days=1)


class AuthProvider:
    def __init__(self, db: ApplicationState):
        self.db = db

    def create_jwt_for_user(self, user: User):
        payload = {
            "name": user.name,
            "email": user.email,
            "exp": datetime.now() + JWT_EXP,
        }
        return jwt.encode(payload, config.AUTH_SECRET_KEY, algorithm="HS256")

    def validate_token(self, token: str) -> Union[User, None]:
        try:
            payload = jwt.decode(token, config.AUTH_SECRET_KEY, algorithms=["HS256"])
            return User(**payload)
        except jwt.exceptions.DecodeError:
            return None

    def hash_pw(self, passwd: str) -> str:
        return bcrypt.hashpw(passwd.encode(), bcrypt.gensalt())

    def check_password(self, email: str, plaintext_password: str) -> Union[User, None]:
        user = get_user_with_email(self.db, email)
        # compare password hashes
        bcrypt.checkpw(plaintext_password.encode(), user.password_hash.encode())

        return user
