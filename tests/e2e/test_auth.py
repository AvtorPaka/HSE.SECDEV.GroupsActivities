import uuid

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.asyncio


async def test_register_successful(client: TestClient):
    unique_email = f"register_success_{uuid.uuid4().hex[:6]}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "username": "test_success_user",
            "email": unique_email,
            "password": "StrongPassword123!",
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_register_duplicate_email(client: TestClient, created_user: dict):
    response = client.post(
        "/auth/register",
        json={
            "username": "another_user",
            "email": created_user["email"],
            "password": "AnotherPassword123!",
        },
    )
    assert response.status_code == 202
    body = response.json()
    assert body["error"]["code"] == "check_provided_email"
