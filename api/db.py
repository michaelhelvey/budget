import json
import os
from datetime import datetime
from typing import Union

from api.config import DB_PATH
from api.domain import ApplicationState, MonthlyState, User

default_state = {
    "users": [],
    "last_accessed": datetime.now().isoformat(),
    "defaults": {
        "monthly_income": 570000,
        "fixed_expenses": [
            {"category": "Mortgage", "amount": 200000},
            {"category": "Insurance", "amount": 20000},
            {"category": "Giving", "amount": 30000},
        ],
    },
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
            maybe_rollover_month(_db)

    return _db

def _delete_db_singleton():
    global _db
    _db = None

def save_state_to_file(state: ApplicationState):
    with open(DB_PATH, "w") as file:
        file.write(state.json())


def maybe_rollover_month(db: ApplicationState, get_now=datetime.now):
    now: datetime = get_now()
    la = db.last_accessed

    if la.month != now.month:
        # create a new month
        new_monthly_state = MonthlyState.new_from_defaults(db.defaults)
        db.state[new_monthly_state.key_for_date(now)] = new_monthly_state


################################################################################
# Database queries
################################################################################


def get_user_with_email(db: ApplicationState, email: str) -> Union[User, None]:
    # yes, this is O(n), but this app is designed to have 1-3 users, lol
    for user in db.users:
        if user.email == email:
            return user

    return None
