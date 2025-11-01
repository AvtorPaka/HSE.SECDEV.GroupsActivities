import asyncio
import os
import sys
import uuid
from asyncio import AbstractEventLoop
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

os.environ["PG_HOST"] = "localhost"
os.environ["PG_DB"] = "test-devsec-studygroups"
os.environ["PG_PORT"] = "5432"
os.environ["PG_MIGRATION_USER"] = "stump"
os.environ["PG_MIGRATION_PSWD"] = "example"
os.environ["PG_APP_USER"] = "test-appuser"
os.environ["PG_APP_PSWD"] = "test-apppassword"

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.hasher.hasher import PasswordHasher  # noqa: E402
from app.infrastructure.dal.configuration.postgres import DATABASE_APP_URL  # noqa: E402
from app.infrastructure.dal.entities.models import User  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def event_loop() -> Generator[AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def db_engine_and_session_factory():
    engine = create_async_engine(DATABASE_APP_URL, echo=False)
    factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    yield engine, factory
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine_and_session_factory) -> AsyncGenerator[AsyncSession, None]:
    engine, factory = db_engine_and_session_factory
    async with factory() as session:
        await session.begin()
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def created_user(db_session: AsyncSession) -> dict:
    user_data = {
        "username": f"testuser_{uuid.uuid4().hex[:6]}",
        "email": f"user_{uuid.uuid4().hex[:6]}@example.com",
        "password": "mySecurePassword123!",
    }
    hashed_password = PasswordHasher.hash_password(user_data["password"])
    db_user = User(
        username=user_data["username"],
        email=user_data["email"],
        password_hashed=hashed_password,
    )
    db_session.add(db_user)
    await db_session.commit()
    await db_session.refresh(db_user)
    user_data["id"] = db_user.id
    return user_data


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c
