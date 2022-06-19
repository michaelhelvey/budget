import os
from api.config import DB_PATH
from api.domain import User
from api.db import get_db_instance, save_state_to_file, _delete_db_singleton
from api.auth import AuthProvider


"""
Utilities for common testing tasks
"""


def util_create_user(name: str, email: str, password: str) -> User:
    db = get_db_instance()
    auth = AuthProvider(db=db)

    user = User(name=name, email=email, password_hash=auth.hash_pw(password))
    db.users.append(user)
    save_state_to_file(db)

    return user

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        _delete_db_singleton()