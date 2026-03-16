import pytest
from datetime import datetime


class TestSettingsGet:
    async def test_get_settings(self, client, auth_header):
        response = await client.get("/api/settings", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "telegram_configured" in data
        assert "vk_configured" in data
        assert "wordpress_configured" in data
        assert "ai_configured" in data

    async def test_get_settings_unauthorized(self, client):
        response = await client.get("/api/settings")
        assert response.status_code == 403


class TestSettingsUpdateKeys:
    async def test_update_api_keys(self, client, auth_header):
        response = await client.post(
            "/api/settings/keys",
            json={
                "glm_api_key": "new-api-key",
                "telegram_bot_token": "new-token",
            },
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "updated"

    async def test_update_all_keys(self, client, auth_header):
        response = await client.post(
            "/api/settings/keys",
            json={
                "glm_api_key": "key",
                "telegram_bot_token": "token",
                "vk_access_token": "vk-token",
                "vk_group_id": 123456,
                "wp_url": "https://example.com",
                "wp_username": "admin",
                "wp_password": "password",
            },
            headers=auth_header,
        )
        assert response.status_code == 200

    async def test_update_keys_empty(self, client, auth_header):
        response = await client.post(
            "/api/settings/keys",
            json={},
            headers=auth_header,
        )
        assert response.status_code == 200


class TestSettingsExport:
    async def test_export_data(
        self, client, auth_header, sample_channel, sample_post, sample_product
    ):
        response = await client.get("/api/settings/export", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "channels" in data
        assert "posts" in data
        assert "products" in data
        assert "exported_at" in data

    async def test_export_data_empty(self, client, auth_header):
        response = await client.get("/api/settings/export", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert len(data["channels"]) == 0
        assert len(data["posts"]) == 0

    async def test_export_unauthorized(self, client):
        response = await client.get("/api/settings/export")
        assert response.status_code == 403


class TestSettingsClearLogs:
    async def test_clear_logs(self, client, auth_header, db):
        response = await client.delete("/api/settings/logs?days=30", headers=auth_header)
        assert response.status_code == 200
        data = response.json()
        assert "deleted_publish_logs" in data
        assert "deleted_censorship_logs" in data
        assert "deleted_analytics" in data

    async def test_clear_logs_custom_days(self, client, auth_header):
        response = await client.delete("/api/settings/logs?days=7", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["older_than_days"] == 7

    async def test_clear_logs_unauthorized(self, client):
        response = await client.delete("/api/settings/logs?days=30")
        assert response.status_code == 403
