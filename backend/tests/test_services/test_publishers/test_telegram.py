import pytest
from unittest.mock import AsyncMock, patch
import respx


class TestTelegramPublisherInit:
    def test_init_with_token(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        assert publisher.token == "123456:ABC"
        assert "123456:ABC" in publisher.base_url

    def test_init_without_token(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token=None)
        assert publisher.token is None


class TestTelegramPublisherSendMessage:
    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_telegram_api):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        result = await publisher.send_message("@testchannel", "Test message")

        assert result["ok"] is True
        assert result["result"]["message_id"] == 123

    @pytest.mark.asyncio
    async def test_send_message_no_token(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token=None)
        result = await publisher.send_message("@testchannel", "Test message")

        assert result["ok"] is False
        assert "error" in result

    @pytest.mark.asyncio
    async def test_send_message_with_parse_mode(self, mock_telegram_api):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        result = await publisher.send_message("@testchannel", "*Bold*", parse_mode="Markdown")

        assert result["ok"] is True


class TestTelegramPublisherSendPhoto:
    @pytest.mark.asyncio
    async def test_send_photo_success(self, mock_telegram_api):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        result = await publisher.send_photo("@testchannel", "https://example.com/photo.jpg")

        assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_send_photo_with_caption(self, mock_telegram_api):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        result = await publisher.send_photo(
            "@testchannel", "https://example.com/photo.jpg", caption="Photo caption"
        )

        assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_send_photo_no_token(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token=None)
        result = await publisher.send_photo("@testchannel", "https://example.com/photo.jpg")

        assert result["ok"] is False


class TestTelegramPublisherSendVideo:
    @pytest.mark.asyncio
    async def test_send_video_success(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")

        with respx.mock(base_url="https://api.telegram.org") as mock:
            mock.post("/bot123456:ABC/sendVideo").mock(
                return_value=respx.Response(200, json={"ok": True, "result": {"message_id": 125}})
            )
            result = await publisher.send_video("@testchannel", "https://example.com/video.mp4")

        assert result["ok"] is True


class TestTelegramPublisherEditMessage:
    @pytest.mark.asyncio
    async def test_edit_message_success(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")

        with respx.mock(base_url="https://api.telegram.org") as mock:
            mock.post("/bot123456:ABC/editMessageText").mock(
                return_value=respx.Response(200, json={"ok": True, "result": True})
            )
            result = await publisher.edit_message("@testchannel", 123, "Updated text")

        assert result["ok"] is True


class TestTelegramPublisherDeleteMessage:
    @pytest.mark.asyncio
    async def test_delete_message_success(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")

        with respx.mock(base_url="https://api.telegram.org") as mock:
            mock.post("/bot123456:ABC/deleteMessage").mock(
                return_value=respx.Response(200, json={"ok": True, "result": True})
            )
            result = await publisher.delete_message("@testchannel", 123)

        assert result["ok"] is True


class TestTelegramPublisherFormatPost:
    def test_format_post_with_title(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher()
        result = publisher.format_post("Title", "Body text")

        assert "Title" in result
        assert "Body text" in result

    def test_format_post_with_source(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher()
        result = publisher.format_post("Title", "Body", "https://example.com")

        assert "Источник" in result
        assert "example.com" in result

    def test_format_post_without_title(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher()
        result = publisher.format_post(None, "Just body text")

        assert "Just body text" in result

    def test_escape_markdown(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher()
        result = publisher._escape_markdown("Text with *bold* and _italic_")

        assert "\\*" in result
        assert "\\_" in result


class TestTelegramPublisherGetMe:
    @pytest.mark.asyncio
    async def test_get_me_success(self, mock_telegram_api):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        result = await publisher.get_me()

        assert result["ok"] is True

    @pytest.mark.asyncio
    async def test_get_me_no_token(self):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token=None)
        result = await publisher.get_me()

        assert result["ok"] is False


class TestTelegramPublisherGetChat:
    @pytest.mark.asyncio
    async def test_get_chat_success(self, mock_telegram_api):
        from app.services.publishers.telegram import TelegramPublisher

        publisher = TelegramPublisher(token="123456:ABC")
        result = await publisher.get_chat("@testchannel")

        assert result["ok"] is True
