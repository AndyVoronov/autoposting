import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models.user import User
from app.utils.security import get_password_hash


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as db:
        admin = User(
            username="testadmin",
            password_hash=get_password_hash("testpass123"),
            is_active=True,
        )
        db.add(admin)
        await db.commit()

        yield db

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def auth_header(client):
    response = await client.post(
        "/api/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


class TestAuth:
    async def test_login_success(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpass123"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_login_wrong_password(self, client):
        response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "wrongpass"},
        )
        assert response.status_code == 401

    async def test_get_current_user(self, client, auth_header):
        response = await client.get("/api/auth/me", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["username"] == "testadmin"

    async def test_unauthorized_access(self, client):
        response = await client.get("/api/auth/me")
        assert response.status_code == 403


class TestChannels:
    async def test_create_channel(self, client, auth_header):
        response = await client.post(
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

    async def test_get_channels(self, client, auth_header):
        await client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )

        response = await client.get("/api/channels", headers=auth_header)
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_update_channel(self, client, auth_header):
        create_response = await client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = create_response.json()["id"]

        response = await client.patch(
            f"/api/channels/{channel_id}",
            json={"name": "Updated Channel"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Channel"

    async def test_delete_channel(self, client, auth_header):
        create_response = await client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = create_response.json()["id"]

        response = await client.delete(f"/api/channels/{channel_id}", headers=auth_header)
        assert response.status_code == 204


class TestPosts:
    async def test_create_post(self, client, auth_header):
        channel_response = await client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = channel_response.json()["id"]

        response = await client.post(
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

    async def test_approve_post(self, client, auth_header):
        channel_response = await client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = channel_response.json()["id"]

        post_response = await client.post(
            "/api/posts",
            json={
                "channel_id": channel_id,
                "body": "Test post content",
                "status": "pending",
            },
            headers=auth_header,
        )
        post_id = post_response.json()["id"]

        response = await client.post(f"/api/posts/{post_id}/approve", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    async def test_reject_post(self, client, auth_header):
        channel_response = await client.post(
            "/api/channels",
            json={
                "name": "Test Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        channel_id = channel_response.json()["id"]

        post_response = await client.post(
            "/api/posts",
            json={
                "channel_id": channel_id,
                "body": "Test post content",
                "status": "pending",
            },
            headers=auth_header,
        )
        post_id = post_response.json()["id"]

        response = await client.post(f"/api/posts/{post_id}/reject", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"
