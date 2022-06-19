import json
import os
from datetime import datetime
from unittest.mock import patch

import pytest
from api.config import BASE_DIR, DB_PATH
from api.db import ensure_exists, get_db_instance, save_state_to_file
from api.domain import ApplicationState, User

from .utils import reset_db


def test_ensure_exists_creates_file():
    path = os.path.join(BASE_DIR, "testing123")

    # make it easier on watch mode:
    if os.path.exists(path):
        os.remove(path)

    with pytest.raises(FileNotFoundError):
        os.stat(path)

    ensure_exists(path)
    assert os.stat(path)

    with open(path, "r") as file:
        assert list(json.loads(file.read()).keys()) == [
            "users",
            "last_accessed",
            "defaults",
            "variable_categories",
            "fixed_categories",
            "state",
        ]

    os.remove(path)


def test_get_db_instance():
    db = get_db_instance()
    db2 = get_db_instance()

    # the loaded db should be cached
    assert db == db2

    # the loaded db should be serialized
    assert isinstance(db.last_accessed, datetime)
    assert isinstance(db, ApplicationState)


def test_can_save_new_state():
    db = get_db_instance()
    db.users = [User(name="Michael", email="michael@1234.com", password_hash="asdf")]
    save_state_to_file(db)

    with open(DB_PATH, "r") as db_file:
        assert json.loads(db_file.read())["users"][0]["email"] == "michael@1234.com"
