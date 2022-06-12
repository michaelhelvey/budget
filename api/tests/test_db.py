import json
import os
from datetime import datetime

import pytest
from unittest.mock import patch

from api.config import BASE_DIR
from api.db import ensure_exists, get_db_instance


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
            "variable_categories",
            "fixed_categories",
            "state",
        ]

    os.remove(path)


def test_get_db_instance():
    path = os.path.join(BASE_DIR, "testing123.json")
    with patch("api.config") as config_mock:
        config_mock.DB_PATH = path
        db = get_db_instance()
        db2 = get_db_instance()

        # the loaded db should be cached
        assert db == db2

        # the loaded db should be serialized
        assert isinstance(db.last_accessed, datetime)
