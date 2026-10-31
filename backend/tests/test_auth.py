"""Auth endpoint tests."""


def test_register_creates_user(client):
    resp = client.post("/auth/register", json={
        "name": "Alice",
        "email": "alice@example.com",
        "password": "securepass1",
    })
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert body["user"]["email"] == "alice@example.com"


def test_register_rejects_duplicate_email(client):
    payload = {"name": "Bob", "email": "bob@example.com", "password": "securepass1"}
    client.post("/auth/register", json=payload)
    resp = client.post("/auth/register", json=payload)
    assert resp.status_code == 400


def test_register_rejects_short_password(client):
    resp = client.post("/auth/register", json={
        "name": "Carol",
        "email": "carol@example.com",
        "password": "short",
    })
    assert resp.status_code == 400


def test_login_returns_token(client):
    client.post("/auth/register", json={
        "name": "Dave",
        "email": "dave@example.com",
        "password": "validpass99",
    })
    resp = client.post("/auth/login", json={
        "email": "dave@example.com",
        "password": "validpass99",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_rejects_wrong_password(client):
    client.post("/auth/register", json={
        "name": "Eve",
        "email": "eve@example.com",
        "password": "correctpass1",
    })
    resp = client.post("/auth/login", json={
        "email": "eve@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


def test_protected_requires_auth(client):
    resp = client.get("/repositories")
    assert resp.status_code == 401


def test_get_me_returns_user(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@codepilot.dev"


def test_change_password_requires_current_password(client, auth_headers):
    response = client.post(
        "/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "wrong-password",
            "new_password": "new-password-123",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Current password is incorrect."


def test_change_password_updates_credentials(client, auth_headers):
    response = client.post(
        "/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "testpassword123",
            "new_password": "new-password-123",
        },
    )

    assert response.status_code == 204
    assert client.post(
        "/auth/login",
        json={"email": "test@codepilot.dev", "password": "new-password-123"},
    ).status_code == 200
    assert client.post(
        "/auth/login",
        json={"email": "test@codepilot.dev", "password": "testpassword123"},
    ).status_code == 401
