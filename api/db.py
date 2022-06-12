import os
import json
from datetime import datetime

from api.config import DB_PATH
from api.domain import ApplicationState

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
