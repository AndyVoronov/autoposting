import pytest
from datetime import datetime


class TestPostsList:
    async def test_get_posts_empty(self, client, auth_header):
        response = await client.get("/api/posts", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_posts_with_data(self, client, auth_header, sample_post):
        response = await client.get("/api/posts", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Post"

    async def test_get_posts_filter_by_status(self, client, auth_header, sample_post):
        response = await client.get("/api/posts?status=draft", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert all(p["status"] == "draft" for p in data)

    async def test_get_posts_filter_by_channel(
        self, client, auth_header, sample_post, sample_channel
    ):
        response = await client.get(
            f"/api/posts?channel_id={sample_channel.id}", headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert all(p["channel_id"] == sample_channel.id for p in data)

    async def test_get_posts_pagination(self, client, auth_header, sample_channel, db):
        from app.models.post import Post, PostStatus

        for i in range(20):
            post = Post(
                channel_id=sample_channel.id,
                title=f"Post {i}",
                body=f"Body {i}",
                status=PostStatus.DRAFT,
            )
            db.add(post)
        await db.commit()

        response = await client.get("/api/posts?skip=5&limit=10", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 10

    async def test_get_posts_unauthorized(self, client):
        response = await client.get("/api/posts")
        assert response.status_code == 403


class TestPostCreate:
    async def test_create_post(self, client, auth_header, sample_channel):
        response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "New Post",
                "body": "This is a new post",
                "status": "draft",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Post"
        assert data["status"] == "draft"

    async def test_create_post_with_media(self, client, auth_header, sample_channel):
        response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "Post with Media",
                "body": "Content",
                "media_urls": ["https://example.com/image.jpg"],
                "status": "draft",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert len(response.json()["media_urls"]) == 1

    async def test_create_post_with_source(self, client, auth_header, sample_channel):
        response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "Sourced Post",
                "body": "Content from source",
                "source_url": "https://reddit.com/r/test/123",
                "source_title": "Original Title",
                "status": "pending",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["source_url"] == "https://reddit.com/r/test/123"

    async def test_create_post_missing_body(self, client, auth_header, sample_channel):
        response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "No body",
            },
            headers=auth_header,
        )
        assert response.status_code == 422

    async def test_create_post_with_ai_metadata(self, client, auth_header, sample_channel):
        response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "AI Generated",
                "body": "Content",
                "ai_metadata": {"translated": True, "rewritten": True},
                "status": "draft",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["ai_metadata"]["translated"] is True


class TestPostGet:
    async def test_get_post_by_id(self, client, auth_header, sample_post):
        response = await client.get(f"/api/posts/{sample_post.id}", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_post.id
        assert data["title"] == "Test Post"

    async def test_get_post_not_found(self, client, auth_header):
        response = await client.get("/api/posts/9999", headers=auth_header)
        assert response.status_code == 404


class TestPostUpdate:
    async def test_update_post_title(self, client, auth_header, sample_post):
        response = await client.patch(
            f"/api/posts/{sample_post.id}",
            json={"title": "Updated Title"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    async def test_update_post_body(self, client, auth_header, sample_post):
        response = await client.patch(
            f"/api/posts/{sample_post.id}",
            json={"body": "Updated body content"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["body"] == "Updated body content"

    async def test_update_post_status(self, client, auth_header, sample_post):
        response = await client.patch(
            f"/api/posts/{sample_post.id}",
            json={"status": "pending"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    async def test_update_post_not_found(self, client, auth_header):
        response = await client.patch(
            "/api/posts/9999",
            json={"title": "Updated"},
            headers=auth_header,
        )
        assert response.status_code == 404


class TestPostDelete:
    async def test_delete_post(self, client, auth_header, sample_post):
        response = await client.delete(f"/api/posts/{sample_post.id}", headers=auth_header)
        assert response.status_code == 204

        response = await client.get(f"/api/posts/{sample_post.id}", headers=auth_header)
        assert response.status_code == 404

    async def test_delete_post_not_found(self, client, auth_header):
        response = await client.delete("/api/posts/9999", headers=auth_header)
        assert response.status_code == 404


class TestPostApprove:
    async def test_approve_post(self, client, auth_header, sample_post):
        sample_post.status = "pending"
        from app.database import async_session_maker

        async with async_session_maker() as db:
            db.add(sample_post)
            await db.commit()

        response = await client.post(f"/api/posts/{sample_post.id}/approve", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "approved"

    async def test_approve_post_not_found(self, client, auth_header):
        response = await client.post("/api/posts/9999/approve", headers=auth_header)
        assert response.status_code == 404


class TestPostReject:
    async def test_reject_post(self, client, auth_header, sample_post):
        sample_post.status = "pending"
        from app.database import async_session_maker

        async with async_session_maker() as db:
            db.add(sample_post)
            await db.commit()

        response = await client.post(f"/api/posts/{sample_post.id}/reject", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "rejected"

    async def test_reject_post_not_found(self, client, auth_header):
        response = await client.post("/api/posts/9999/reject", headers=auth_header)
        assert response.status_code == 404
