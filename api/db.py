import json
import os
from datetime import datetime
from typing import Union

from api.config import DB_PATH
from api.domain import ApplicationState, User

default_state = {
    "users": [],
    "last_accessed": datetime.now().isoformat(),
    "variable_categories": ["Grocery", "Gas", "Utilities", "Michael/Misc", "Anna/Misc"],
    "fixed_categories": ["Mortgage", "Insurance", "Giving"],
    "state": {},
}


def ensure_exists(path: str):
    try:
        os.stat(path)
    except FileNotFoundError:
        with open(path, "w") as file:
            file.write(json.dumps(default_state))


_db = None


def get_db_instance() -> ApplicationState:
    global _db
    if not _db:
        ensure_exists(DB_PATH)
        with open(DB_PATH, "r") as file:
            json_object = json.loads(file.read())
            _db = ApplicationState(**json_object)

    return _db


################################################################################
# Database queries
################################################################################


def get_user_with_email(db: ApplicationState, email: str) -> Union[User, None]:
    # yes, this is O(n), but this app is designed to have 1-3 users, lol
    for user in db.users:
        if user.email == email:
            return user

    return None
