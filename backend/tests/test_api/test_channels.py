import pytest


class TestChannelsList:
    async def test_get_channels_empty(self, client, auth_header):
        response = await client.get("/api/channels", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_channels_with_data(self, client, auth_header, sample_channel):
        response = await client.get("/api/channels", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Channel"

    async def test_get_channels_unauthorized(self, client):
        response = await client.get("/api/channels")
        assert response.status_code == 403

    async def test_get_channels_pagination(self, client, auth_header, db):
        for i in range(15):
            from app.models.channel import Channel, Platform

            channel = Channel(
                name=f"Channel {i}",
                slug=f"channel-{i}",
                platform=Platform.TELEGRAM,
            )
            db.add(channel)
        await db.commit()

        response = await client.get("/api/channels?skip=5&limit=5", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5


class TestChannelCreate:
    async def test_create_channel(self, client, auth_header):
        response = await client.post(
            "/api/channels",
            json={
                "name": "New Channel",
                "slug": "new-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Channel"
        assert data["slug"] == "new-channel"
        assert data["platform"] == "telegram"

    async def test_create_channel_vk(self, client, auth_header):
        response = await client.post(
            "/api/channels",
            json={
                "name": "VK Channel",
                "slug": "vk-channel",
                "platform": "vk",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["platform"] == "vk"

    async def test_create_channel_wordpress(self, client, auth_header):
        response = await client.post(
            "/api/channels",
            json={
                "name": "WordPress Channel",
                "slug": "wp-channel",
                "platform": "wordpress",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["platform"] == "wordpress"

    async def test_create_channel_duplicate_slug(self, client, auth_header, sample_channel):
        response = await client.post(
            "/api/channels",
            json={
                "name": "Another Channel",
                "slug": "test-channel",
                "platform": "telegram",
            },
            headers=auth_header,
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    async def test_create_channel_missing_fields(self, client, auth_header):
        response = await client.post(
            "/api/channels",
            json={"name": "No Slug"},
            headers=auth_header,
        )
        assert response.status_code == 422

    async def test_create_channel_with_config(self, client, auth_header):
        response = await client.post(
            "/api/channels",
            json={
                "name": "Configured Channel",
                "slug": "configured-channel",
                "platform": "telegram",
                "config": {"chat_id": "@mychannel", "notifications": True},
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["config"]["chat_id"] == "@mychannel"


class TestChannelGet:
    async def test_get_channel_by_id(self, client, auth_header, sample_channel):
        response = await client.get(f"/api/channels/{sample_channel.id}", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_channel.id
        assert data["name"] == "Test Channel"

    async def test_get_channel_not_found(self, client, auth_header):
        response = await client.get("/api/channels/9999", headers=auth_header)
        assert response.status_code == 404

    async def test_get_channel_unauthorized(self, client, sample_channel):
        response = await client.get(f"/api/channels/{sample_channel.id}")
        assert response.status_code == 403


class TestChannelUpdate:
    async def test_update_channel_name(self, client, auth_header, sample_channel):
        response = await client.patch(
            f"/api/channels/{sample_channel.id}",
            json={"name": "Updated Channel"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Channel"

    async def test_update_channel_config(self, client, auth_header, sample_channel):
        response = await client.patch(
            f"/api/channels/{sample_channel.id}",
            json={"config": {"chat_id": "@updated"}},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["config"]["chat_id"] == "@updated"

    async def test_update_channel_is_active(self, client, auth_header, sample_channel):
        response = await client.patch(
            f"/api/channels/{sample_channel.id}",
            json={"is_active": False},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    async def test_update_channel_not_found(self, client, auth_header):
        response = await client.patch(
            "/api/channels/9999",
            json={"name": "Updated"},
            headers=auth_header,
        )
        assert response.status_code == 404

    async def test_update_channel_empty_body(self, client, auth_header, sample_channel):
        response = await client.patch(
            f"/api/channels/{sample_channel.id}",
            json={},
            headers=auth_header,
        )
        assert response.status_code == 200


class TestChannelDelete:
    async def test_delete_channel(self, client, auth_header, sample_channel):
        response = await client.delete(f"/api/channels/{sample_channel.id}", headers=auth_header)
        assert response.status_code == 204

        response = await client.get(f"/api/channels/{sample_channel.id}", headers=auth_header)
        assert response.status_code == 404

    async def test_delete_channel_not_found(self, client, auth_header):
        response = await client.delete("/api/channels/9999", headers=auth_header)
        assert response.status_code == 404

    async def test_delete_channel_unauthorized(self, client, sample_channel):
        response = await client.delete(f"/api/channels/{sample_channel.id}")
        assert response.status_code == 403
