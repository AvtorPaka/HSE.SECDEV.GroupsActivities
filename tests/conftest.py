# tests/conftest.py
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

os.environ["PG_DB"] = "test_db"
os.environ["PG_MIGRATION_USER"] = "test_user"
os.environ["PG_MIGRATION_PSWD"] = "test_password"
os.environ["PG_APP_USER"] = "test_user"
os.environ["PG_APP_PSWD"] = "test_password"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def client():
    """
    Yield a TestClient instance for the app.
    """
    with TestClient(app) as c:
        yield c
