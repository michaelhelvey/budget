import pytest
import os

from api.config import BASE_DIR
from api.tests.utils import reset_db

"""
Tests bootstrapping
"""



@pytest.fixture(scope="module", autouse=True)
def reset_database_after_tests():
    yield
    # when tests are done, remove the database so each test run starts with a new state
    reset_db()
