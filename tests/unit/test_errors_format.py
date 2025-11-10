import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_current_user
from app.domain.models.user import UserModel
from app.main import app

BAD_REQUEST_ERROR_BODY = {"error": {"status": "bad_request", "title": "Validation failed"}}

INVALID_CREDENTIALS_ERROR_BODY = {
    "error": {"status": "invalid_credentials", "title": "Invalid credentials provided"}
}


@pytest.fixture
def mock_current_user_model() -> UserModel:
    """Фикстура, которая создает объект пользователя для мока."""
    return UserModel(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hashed="$2b$12$E4.V5.88a/04arafpzO.de./1s34.L5p2.68J5Q3kI/256xte0PXC",
    )


@pytest.fixture
def client_with_mocked_user(mock_current_user_model: UserModel) -> TestClient:
    """
    Фикстура, которая создает клиент API, где зависимость get_current_user
    заменена на мок, возвращающий фейкового пользователя.
    """

    async def mock_get_current_user() -> UserModel:
        return mock_current_user_model

    app.dependency_overrides[get_current_user] = mock_get_current_user

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestChangePasswordValidation:
    def test_change_password_with_invalid_current_password(
        self, client_with_mocked_user: TestClient
    ):
        change_payload = {
            "current_password": "wrong_password",
            "new_password": "a_valid_new_password",
        }
        response = client_with_mocked_user.patch("/users/change-password", json=change_payload)

        assert response.status_code == 200

        response_body = response.json()
        response_body["error"].pop("correlation_id", None)

        assert response_body == INVALID_CREDENTIALS_ERROR_BODY

    def test_change_password_new_password_is_too_short(self, client_with_mocked_user: TestClient):
        change_payload = {"current_password": "password", "new_password": "short"}
        response = client_with_mocked_user.patch("/users/change-password", json=change_payload)

        assert response.status_code == 400
        response_body = response.json()
        response_body["error"].pop("correlation_id", None)

        expected_detail = "New password must be at least 6 characters"
        assert "details" in response_body["error"]
        assert expected_detail in response_body["error"]["details"]

        del response_body["error"]["details"]
        assert response_body == BAD_REQUEST_ERROR_BODY


class TestChangeEmailValidation:
    def test_change_email_invalid_new_email(
        self, client_with_mocked_user: TestClient, mock_current_user_model: UserModel
    ):
        change_payload = {"password": "any_password", "new_email": "invalid-email"}
        response = client_with_mocked_user.patch("/users/change-email", json=change_payload)

        assert response.status_code == 400
        response_body = response.json()
        response_body["error"].pop("correlation_id", None)

        expected_detail = "An email address must have an @-sign."
        assert "details" in response_body["error"]
        assert expected_detail in response_body["error"]["details"]

        del response_body["error"]["details"]
        assert response_body == BAD_REQUEST_ERROR_BODY

    def test_change_email_new_email_is_same_as_current(
        self, client_with_mocked_user: TestClient, mock_current_user_model: UserModel
    ):
        change_payload = {"password": "any_password", "new_email": mock_current_user_model.email}
        response = client_with_mocked_user.patch("/users/change-email", json=change_payload)

        assert response.status_code == 400
        response_body = response.json()
        response_body["error"].pop("correlation_id", None)

        expected_detail = "New email must be different from current."
        assert "details" in response_body["error"]
        assert expected_detail in response_body["error"]["details"]

        del response_body["error"]["details"]
        assert response_body == BAD_REQUEST_ERROR_BODY


class TestRegisterValidation:
    @pytest.mark.parametrize(
        "payload, expected_detail",
        [
            (
                {"username": "", "email": "test@example.com", "password": "password123"},
                "Username is required",
            ),
            (
                {"username": "   ", "email": "test@example.com", "password": "password123"},
                "Username is required",
            ),
            (
                {"username": "a" * 101, "email": "test@example.com", "password": "password123"},
                "Username must be less than 100 characters",
            ),
            (
                {"username": "testuser", "email": "", "password": "password123"},
                "Email is required",
            ),
            (
                {"username": "testuser", "email": "not-an-email", "password": "password123"},
                "An email address must have an @-sign.",
            ),
            (
                {"username": "testuser", "email": "test@invalid", "password": "password123"},
                "The part after the @-sign is not valid. It should have a period.",
            ),
            (
                {"username": "testuser", "email": "test@example.com", "password": ""},
                "Password is required",
            ),
            (
                {"username": "testuser", "email": "test@example.com", "password": "123"},
                "Password must be at least 6 characters",
            ),
        ],
    )
    def test_register_single_field_invalid(
        self, client: TestClient, payload: dict, expected_detail: str
    ):
        response = client.post("/auth/register", json=payload)

        assert response.status_code == 400
        response_body = response.json()

        assert "details" in response_body["error"]
        assert expected_detail in response_body["error"]["details"]
        response_body["error"].pop("correlation_id", None)

        del response_body["error"]["details"]
        assert response_body == BAD_REQUEST_ERROR_BODY

    def test_register_multiple_fields_invalid(self, client: TestClient):
        payload = {"username": "", "email": "not-an-email", "password": "123"}

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 400
        response_body = response.json()

        assert "details" in response_body["error"]
        details = response_body["error"]["details"]
        response_body["error"].pop("correlation_id", None)

        assert "Username is required" in details
        assert "An email address must have an @-sign." in details
        assert "Password must be at least 6 characters" in details

        del response_body["error"]["details"]
        assert response_body == BAD_REQUEST_ERROR_BODY


class TestLoginValidation:
    @pytest.mark.parametrize(
        "payload, expected_details",
        [
            (
                {"email": "", "password": "password123"},
                ["Email is required"],
            ),
            (
                {"email": "test@example.com", "password": ""},
                ["Password is required"],
            ),
            (
                {"email": "", "password": ""},
                ["Email is required", "Password is required"],
            ),
        ],
    )
    def test_login_invalid_credentials(
        self, client: TestClient, payload: dict, expected_details: list[str]
    ):
        response = client.post("/auth/login", json=payload)

        assert response.status_code == 400
        response_body = response.json()

        response_body["error"].pop("correlation_id", None)

        assert "details" in response_body["error"]
        assert set(response_body["error"]["details"]) == set(expected_details)

        del response_body["error"]["details"]
        assert response_body == BAD_REQUEST_ERROR_BODY
