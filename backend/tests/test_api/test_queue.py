import pytest
from datetime import datetime, timedelta


class TestQueueList:
    async def test_get_queue_empty(self, client, auth_header):
        response = await client.get("/api/queue", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_queue_with_data(self, client, auth_header, sample_queue_item):
        response = await client.get("/api/queue", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    async def test_get_queue_filter_by_status(self, client, auth_header, sample_queue_item):
        response = await client.get("/api/queue?status=pending", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert all(q["status"] == "pending" for q in data)

    async def test_get_queue_unauthorized(self, client):
        response = await client.get("/api/queue")
        assert response.status_code == 403


class TestQueueAdd:
    async def test_add_to_queue(self, client, auth_header, sample_post):
        response = await client.post(
            "/api/queue",
            json={
                "post_id": sample_post.id,
                "platform": "telegram",
                "scheduled_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["post_id"] == sample_post.id
        assert data["platform"] == "telegram"
        assert data["status"] == "pending"

    async def test_add_to_queue_vk(self, client, auth_header, sample_post):
        response = await client.post(
            "/api/queue",
            json={
                "post_id": sample_post.id,
                "platform": "vk",
                "scheduled_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["platform"] == "vk"

    async def test_add_to_queue_wordpress(self, client, auth_header, sample_post):
        response = await client.post(
            "/api/queue",
            json={
                "post_id": sample_post.id,
                "platform": "wordpress",
                "scheduled_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["platform"] == "wordpress"

    async def test_add_to_queue_with_priority(self, client, auth_header, sample_post):
        response = await client.post(
            "/api/queue",
            json={
                "post_id": sample_post.id,
                "platform": "telegram",
                "scheduled_at": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                "priority": 1,
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["priority"] == 1


class TestQueueRemove:
    async def test_remove_from_queue(self, client, auth_header, sample_queue_item):
        response = await client.delete(f"/api/queue/{sample_queue_item.id}", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["status"] == "removed"

    async def test_remove_from_queue_not_found(self, client, auth_header):
        response = await client.delete("/api/queue/9999", headers=auth_header)
        assert response.status_code == 200
        assert "error" in response.json()
