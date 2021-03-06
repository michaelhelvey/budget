from typing import Any
import os

ENV = os.getenv("APP_ENV")

class ConfigError(Exception):
    pass


def _config_get(key: str, default: any = None) -> Any:
    is_production = ENV == "production"
    value = os.getenv(key)

    if not value and is_production:
        raise ConfigError(f"Could not find value {value} in env {ENV}")

    return value or default


AUTH_SECRET_KEY = _config_get("AUTH_SECRET_KEY", "1234")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if os.getenv("APP_ENV") == "testing":
    DB_PATH = os.path.join(BASE_DIR, "db_testing.json")
else:
    DB_PATH = _config_get("DB_PATH", os.path.join(BASE_DIR, "db.json"))
