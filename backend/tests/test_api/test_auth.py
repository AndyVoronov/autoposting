import pytest
from datetime import datetime, timedelta


class TestAuthLogin:
    async def test_login_success(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpass123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "wrongpass"},
        )
        assert response.status_code == 401

    async def test_login_wrong_username(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "wronguser", "password": "testpass123"},
        )
        assert response.status_code == 401

    async def test_login_missing_fields(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin"},
        )
        assert response.status_code == 422

    async def test_login_empty_credentials(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "", "password": ""},
        )
        assert response.status_code == 401


class TestAuthMe:
    async def test_get_current_user(self, client, auth_header):
        response = await client.get("/api/auth/me", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testadmin"
        assert data["is_active"] is True

    async def test_unauthorized_access(self, client):
        response = await client.get("/api/auth/me")
        assert response.status_code == 403

    async def test_invalid_token(self, client):
        response = await client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401

    async def test_expired_token(self, client, auth_header):
        response = await client.get("/api/auth/me", headers=auth_header)
        assert response.status_code == 200

    async def test_malformed_auth_header(self, client):
        response = await client.get("/api/auth/me", headers={"Authorization": "invalid_format"})
        assert response.status_code == 403
