def test_register_bad_request_simple_password(client):
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "123"},
    )

    assert response.status_code == 400, f"Expected status 400, but got {response.status_code}"

    body = response.json()

    assert "error" in body
    assert body["error"]["code"] == "bad_request"
