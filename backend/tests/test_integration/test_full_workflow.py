import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch


class TestFullWorkflow:
    @pytest.mark.asyncio
    async def test_create_channel_and_post_flow(self, client, auth_header):
        channel_response = await client.post(
            "/api/channels",
            json={
                "name": "Integration Test Channel",
                "slug": "integration-test-channel",
                "platform": "telegram",
                "config": {"chat_id": "@testchannel"},
            },
            headers=auth_header,
        )
        assert channel_response.status_code == 201
        channel_id = channel_response.json()["id"]

        post_response = await client.post(
            "/api/posts",
            json={
                "channel_id": channel_id,
                "title": "Integration Test Post",
                "body": "This is an integration test post content.",
                "status": "draft",
            },
            headers=auth_header,
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]

        get_post_response = await client.get(f"/api/posts/{post_id}", headers=auth_header)
        assert get_post_response.status_code == 200
        assert get_post_response.json()["title"] == "Integration Test Post"

        delete_response = await client.delete(f"/api/posts/{post_id}", headers=auth_header)
        assert delete_response.status_code == 204

        delete_channel_response = await client.delete(
            f"/api/channels/{channel_id}", headers=auth_header
        )
        assert delete_channel_response.status_code == 204


class TestPostModerationFlow:
    @pytest.mark.asyncio
    async def test_approve_post_flow(self, client, auth_header, sample_channel):
        post_response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "Post to Approve",
                "body": "Content for approval",
                "status": "pending",
            },
            headers=auth_header,
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]

        approve_response = await client.post(f"/api/posts/{post_id}/approve", headers=auth_header)
        assert approve_response.status_code == 200
        assert approve_response.json()["status"] == "approved"

        get_response = await client.get(f"/api/posts/{post_id}", headers=auth_header)
        assert get_response.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_reject_post_flow(self, client, auth_header, sample_channel):
        post_response = await client.post(
            "/api/posts",
            json={
                "channel_id": sample_channel.id,
                "title": "Post to Reject",
                "body": "Content for rejection",
                "status": "pending",
            },
            headers=auth_header,
        )
        assert post_response.status_code == 201
        post_id = post_response.json()["id"]

        reject_response = await client.post(f"/api/posts/{post_id}/reject", headers=auth_header)
        assert reject_response.status_code == 200
        assert reject_response.json()["status"] == "rejected"


class TestCensorshipFlow:
    @pytest.mark.asyncio
    async def test_create_rule_and_check_text(self, client, auth_header):
        rule_response = await client.post(
            "/api/censorship/rules",
            json={
                "pattern": "forbidden_test_word",
                "pattern_type": "word",
                "rule_type": "banned",
                "category": "test",
            },
            headers=auth_header,
        )
        assert rule_response.status_code == 200

        check_response = await client.post(
            "/api/censorship/check",
            json={"text": "This contains forbidden_test_word in it"},
            headers=auth_header,
        )
        assert check_response.status_code == 200
        data = check_response.json()
        assert data["passed"] is False


class TestQueueWorkflow:
    @pytest.mark.asyncio
    async def test_schedule_and_cancel_post(self, client, auth_header, sample_channel, sample_post):
        queue_response = await client.post(
            "/api/queue",
            json={
                "post_id": sample_post.id,
                "platform": "telegram",
                "scheduled_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            },
            headers=auth_header,
        )
        assert queue_response.status_code == 200
        queue_id = queue_response.json()["id"]

        queue_list_response = await client.get("/api/queue", headers=auth_header)
        assert queue_list_response.status_code == 200
        assert len(queue_list_response.json()) >= 1

        remove_response = await client.delete(f"/api/queue/{queue_id}", headers=auth_header)
        assert remove_response.status_code == 200


class TestContentTypeBinding:
    @pytest.mark.asyncio
    async def test_create_and_bind_content_type(self, client, auth_header, sample_channel):
        ct_response = await client.post(
            "/api/content-types",
            json={
                "name": "Test Content Type",
                "type": "custom",
                "description": "For testing",
            },
            headers=auth_header,
        )
        assert ct_response.status_code == 201
        ct_id = ct_response.json()["id"]

        bind_response = await client.post(
            f"/api/content-types/{ct_id}/channels",
            json={
                "channel_id": sample_channel.id,
                "schedule": "0 * * * *",
            },
            headers=auth_header,
        )
        assert bind_response.status_code == 201

        channels_response = await client.get(
            f"/api/content-types/{ct_id}/channels", headers=auth_header
        )
        assert channels_response.status_code == 200
        assert len(channels_response.json()) == 1


class TestProductWorkflow:
    @pytest.mark.asyncio
    async def test_create_update_delete_product(self, client, auth_header):
        create_response = await client.post(
            "/api/products",
            json={
                "name": "Integration Test Product",
                "category": "test",
                "ref_url": "https://example.com/test-product",
                "description": "Test product for integration tests",
            },
            headers=auth_header,
        )
        assert create_response.status_code == 200
        product_id = create_response.json()["id"]

        update_response = await client.patch(
            f"/api/products/{product_id}",
            json={"name": "Updated Product Name"},
            headers=auth_header,
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Updated Product Name"

        delete_response = await client.delete(f"/api/products/{product_id}", headers=auth_header)
        assert delete_response.status_code == 200


class TestAnalyticsFlow:
    @pytest.mark.asyncio
    async def test_dashboard_stats_after_posts(
        self, client, auth_header, sample_channel, sample_post, db
    ):
        from app.models.analytics import Analytics
        from app.models.post import PostStatus

        sample_post.status = PostStatus.PUBLISHED
        sample_post.published_at = datetime.utcnow()
        await db.commit()

        analytics = Analytics(
            post_id=sample_post.id,
            platform="telegram",
            views=500,
            likes=25,
            clicks=50,
        )
        db.add(analytics)
        await db.commit()

        response = await client.get("/api/analytics/dashboard", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["total_views"] >= 500
        assert data["total_clicks"] >= 50


class TestAuthenticationFlow:
    @pytest.mark.asyncio
    async def test_full_auth_cycle(self, client):
        login_response = await client.post(
            "/api/auth/login",
            json={"username": "testadmin", "password": "testpass123"},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        me_response = await client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["username"] == "testadmin"

        channels_response = await client.get("/api/channels", headers=headers)
        assert channels_response.status_code == 200
