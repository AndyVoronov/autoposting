import pytest
from unittest.mock import AsyncMock, patch


class TestVKPublisherInit:
    def test_init_with_credentials(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token="test-token", group_id=123456)
        assert publisher.access_token == "test-token"
        assert publisher.group_id == 123456

    def test_init_without_credentials(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token=None, group_id=None)
        assert publisher.access_token is None
        assert publisher.group_id is None


class TestVKPublisherWallPost:
    @pytest.mark.asyncio
    async def test_wall_post_success(self, mock_vk_api):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token="test-token", group_id=123456)
        result = await publisher.wall_post("Test message")

        assert result["success"] is True
        assert result["post_id"] == 123

    @pytest.mark.asyncio
    async def test_wall_post_no_credentials(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token=None, group_id=None)
        result = await publisher.wall_post("Test message")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_wall_post_with_attachments(self, mock_vk_api):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token="test-token", group_id=123456)
        result = await publisher.wall_post("Test", attachments=["photo123_456"])

        assert result["success"] is True


class TestVKPublisherGetUploadServer:
    @pytest.mark.asyncio
    async def test_get_upload_server_success(self, mock_vk_api):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token="test-token", group_id=123456)
        result = await publisher.get_upload_server()

        assert "response" in result

    @pytest.mark.asyncio
    async def test_get_upload_server_no_credentials(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token=None, group_id=None)
        result = await publisher.get_upload_server()

        assert "error" in result


class TestVKPublisherGetGroupInfo:
    @pytest.mark.asyncio
    async def test_get_group_info_success(self, mock_vk_api):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token="test-token", group_id=123456)
        result = await publisher.get_group_info()

        assert "response" in result
        assert result["response"][0]["name"] == "Test Group"

    @pytest.mark.asyncio
    async def test_get_group_info_no_credentials(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher(access_token=None, group_id=None)
        result = await publisher.get_group_info()

        assert "error" in result


class TestVKPublisherFormatPost:
    def test_format_post_with_title(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher()
        result = publisher.format_post("Title", "Body content")

        assert "Title" in result
        assert "Body content" in result

    def test_format_post_without_title(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher()
        result = publisher.format_post(None, "Body content")

        assert "Body content" in result

    def test_format_post_with_source(self):
        from app.services.publishers.vk import VKPublisher

        publisher = VKPublisher()
        result = publisher.format_post("Title", "Body", "https://example.com")

        assert "https://example.com" in result
