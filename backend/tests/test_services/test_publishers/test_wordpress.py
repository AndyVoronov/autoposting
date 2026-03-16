import pytest
from unittest.mock import AsyncMock, patch


class TestWordPressPublisherInit:
    def test_init_with_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        assert publisher.url == "https://example.com"
        assert publisher.username == "admin"
        assert publisher.password == "password"

    def test_init_without_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        assert publisher.url == ""
        assert publisher.username is None
        assert publisher.password is None

    def test_url_trailing_slash_removed(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url="https://example.com/")
        assert publisher.url == "https://example.com"


class TestWordPressPublisherAuth:
    def test_auth_with_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        assert publisher.auth == ("admin", "password")

    def test_auth_without_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        assert publisher.auth is None


class TestWordPressPublisherCreatePost:
    @pytest.mark.asyncio
    async def test_create_post_success(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        result = await publisher.create_post(
            title="Test Post", content="<p>Test content</p>", status="publish"
        )

        assert result["success"] is True
        assert result["post_id"] == 123

    @pytest.mark.asyncio
    async def test_create_post_no_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        result = await publisher.create_post("Title", "Content")

        assert "error" in result

    @pytest.mark.asyncio
    async def test_create_post_with_categories(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        result = await publisher.create_post(title="Test", content="Content", categories=[1, 2])

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_create_draft(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        result = await publisher.create_post(title="Draft", content="Content", status="draft")

        assert result["success"] is True


class TestWordPressPublisherGetCategories:
    @pytest.mark.asyncio
    async def test_get_categories_success(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        result = await publisher.get_categories()

        assert len(result) >= 1
        assert result[0]["name"] == "Uncategorized"

    @pytest.mark.asyncio
    async def test_get_categories_no_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        result = await publisher.get_categories()

        assert result == []


class TestWordPressPublisherUploadMedia:
    @pytest.mark.asyncio
    async def test_upload_media_success(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance

            mock_response = AsyncMock()
            mock_response.content = b"fake_image_data"
            mock_response.raise_for_status = lambda: None
            mock_instance.get.return_value = mock_response

            mock_upload_response = AsyncMock()
            mock_upload_response.json.return_value = {
                "id": 456,
                "source_url": "https://example.com/image.jpg",
            }
            mock_upload_response.raise_for_status = lambda: None
            mock_instance.post.return_value = mock_upload_response

            result = await publisher.upload_media("https://example.com/image.jpg")
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_upload_media_no_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        result = await publisher.upload_media("https://example.com/image.jpg")

        assert "error" in result


class TestWordPressPublisherUpdatePost:
    @pytest.mark.asyncio
    async def test_update_post_success(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        result = await publisher.update_post(123, title="Updated Title")

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_update_post_no_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        result = await publisher.update_post(123, title="Updated")

        assert "error" in result


class TestWordPressPublisherDeletePost:
    @pytest.mark.asyncio
    async def test_delete_post_success(self, mock_wordpress_api):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(
            url="https://example.com", username="admin", password="password"
        )
        result = await publisher.delete_post(123)

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_delete_post_no_credentials(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher(url=None, username=None, password=None)
        result = await publisher.delete_post(123)

        assert "error" in result


class TestWordPressPublisherFormatContent:
    def test_format_content_with_source(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher()
        result = publisher.format_content("Title", "Body", "https://example.com")

        assert "<h2>Title</h2>" in result
        assert "Body" in result
        assert "https://example.com" in result

    def test_format_content_without_source(self):
        from app.services.publishers.wordpress import WordPressPublisher

        publisher = WordPressPublisher()
        result = publisher.format_content("Title", "Body")

        assert "<h2>Title</h2>" in result
        assert "Body" in result
        assert "Источник" not in result
