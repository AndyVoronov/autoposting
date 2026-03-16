import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import get_password_hash


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    admin = User(
        username="testadmin",
        password_hash=get_password_hash("testpass123"),
        is_active=True,
    )
    db.add(admin)
    db.commit()

    yield db

    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    return TestClient(app)


@pytest.fixture(scope="function")
def auth_header(client):
    response = client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    def test_login_success(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_wrong_password(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "wrongpass"},
        )
        assert response.status_code == 401

    def test_get_current_user(self, client, auth_header):
        response = client.get("/api/auth/me", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["username"] == "testadmin"

    def test_unauthorized_access(self, client):
        response = client.get("/api/auth/me")
        assert response.status_code == 403


class TestChannels:
    def test_create_channel(self, client, auth_header):
        response = client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Test Channel"

    def test_get_channels(self, client, auth_header):
        client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )

        response = client.get("/api/channels", headers=auth_header)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_update_channel(self, client, auth_header):
        create_response = client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = create_response.json()["id"]

        response = client.patch(
            f"/api/channels/{channel_id}",
            json={"name": "Updated Channel"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Channel"

    def test_delete_channel(self, client, auth_header):
        create_response = client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = create_response.json()["id"]

        response = client.delete(f"/api/channels/{channel_id}", headers=auth_header)
        assert response.status_code == 204


class TestPosts:
    def test_create_post(self, client, auth_header):
        channel_response = client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = channel_response.json()["id"]

        response = client.post(
            "/api/posts",
            json={
                "channel_id": channel_id,
                "body": "Test post content",
                "status": "draft",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["body"] == "Test post content"

    def test_approve_post(self, client, auth_header):
        channel_response = client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = channel_response.json()["id"]

        post_response = client.post(
            "/api/posts",
            json={
                "channel_id": channel_id,
                "body": "Test post content",
                "status": "pending",
            },
            headers=auth_header,
        )
        post_id = post_response.json()["id"]

        response = client.post(f"/api/posts/{post_id}/approve", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    def test_reject_post(self, client, auth_header):
        channel_response = client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = channel_response.json()["id"]

        post_response = client.post(
            "/api/posts",
            json={
                "channel_id": channel_id,
                "body": "Test post content",
                "status": "pending",
            },
            headers=auth_header,
        )
        post_id = post_response.json()["id"]

        response = client.post(f"/api/posts/{post_id}/reject", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"
