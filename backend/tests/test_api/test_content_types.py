import pytest


class TestContentTypesList:
    async def test_get_content_types_empty(self, client, auth_header):
        response = await client.get("/api/content-types", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_content_types_with_data(self, client, auth_header, sample_content_type):
        response = await client.get("/api/content-types", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Reddit Content"

    async def test_get_content_types_unauthorized(self, client):
        response = await client.get("/api/content-types")
        assert response.status_code == 403


class TestContentTypeCreate:
    async def test_create_content_type(self, client, auth_header):
        response = await client.post(
            "/api/content-types",
            json={
                "name": "Horoscope Content",
                "type": "horoscope",
                "description": "Daily horoscopes",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Horoscope Content"
        assert data["type"] == "horoscope"

    async def test_create_content_type_news(self, client, auth_header):
        response = await client.post(
            "/api/content-types",
            json={
                "name": "News Feed",
                "type": "news",
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        assert response.json()["type"] == "news"

    async def test_create_content_type_with_config(self, client, auth_header):
        response = await client.post(
            "/api/content-types",
            json={
                "name": "Custom Reddit",
                "type": "reddit",
                "config": {"subreddit": "python", "min_score": 1000},
            },
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["config"]["subreddit"] == "python"

    async def test_create_content_type_missing_type(self, client, auth_header):
        response = await client.post(
            "/api/content-types",
            json={"name": "No Type"},
            headers=auth_header,
        )
        assert response.status_code == 422


class TestContentTypeGet:
    async def test_get_content_type_by_id(self, client, auth_header, sample_content_type):
        response = await client.get(
            f"/api/content-types/{sample_content_type.id}", headers=auth_header
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_content_type.id

    async def test_get_content_type_not_found(self, client, auth_header):
        response = await client.get("/api/content-types/9999", headers=auth_header)
        assert response.status_code == 404


class TestContentTypeUpdate:
    async def test_update_content_type(self, client, auth_header, sample_content_type):
        response = await client.patch(
            f"/api/content-types/{sample_content_type.id}",
            json={"name": "Updated Name"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    async def test_update_content_type_is_active(self, client, auth_header, sample_content_type):
        response = await client.patch(
            f"/api/content-types/{sample_content_type.id}",
            json={"is_active": False},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    async def test_update_content_type_not_found(self, client, auth_header):
        response = await client.patch(
            "/api/content-types/9999",
            json={"name": "Updated"},
            headers=auth_header,
        )
        assert response.status_code == 404


class TestContentTypeDelete:
    async def test_delete_content_type(self, client, auth_header, sample_content_type):
        response = await client.delete(
            f"/api/content-types/{sample_content_type.id}", headers=auth_header
        )
        assert response.status_code == 204

    async def test_delete_content_type_not_found(self, client, auth_header):
        response = await client.delete("/api/content-types/9999", headers=auth_header)
        assert response.status_code == 404


class TestChannelBinding:
    async def test_get_content_type_channels_empty(self, client, auth_header, sample_content_type):
        response = await client.get(
            f"/api/content-types/{sample_content_type.id}/channels", headers=auth_header
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_bind_channel_to_content_type(
        self, client, auth_header, sample_content_type, sample_channel
    ):
        response = await client.post(
            f"/api/content-types/{sample_content_type.id}/channels",
            json={"channel_id": sample_channel.id, "schedule": "0 * * * *"},
            headers=auth_header,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["channel_id"] == sample_channel.id
        assert data["schedule"] == "0 * * * *"

    async def test_bind_channel_duplicate(
        self, client, auth_header, sample_content_type, sample_channel, db
    ):
        from app.models.channel import ChannelContent

        binding = ChannelContent(
            channel_id=sample_channel.id,
            content_type_id=sample_content_type.id,
            is_active=True,
        )
        db.add(binding)
        await db.commit()

        response = await client.post(
            f"/api/content-types/{sample_content_type.id}/channels",
            json={"channel_id": sample_channel.id},
            headers=auth_header,
        )
        assert response.status_code == 400

    async def test_bind_channel_not_found(self, client, auth_header, sample_content_type):
        response = await client.post(
            f"/api/content-types/{sample_content_type.id}/channels",
            json={"channel_id": 9999},
            headers=auth_header,
        )
        assert response.status_code == 404

    async def test_unbind_channel(
        self, client, auth_header, sample_content_type, sample_channel, db
    ):
        from app.models.channel import ChannelContent

        binding = ChannelContent(
            channel_id=sample_channel.id,
            content_type_id=sample_content_type.id,
            is_active=True,
        )
        db.add(binding)
        await db.commit()
        await db.refresh(binding)

        response = await client.delete(
            f"/api/content-types/{sample_content_type.id}/channels/{binding.id}",
            headers=auth_header,
        )
        assert response.status_code == 204
