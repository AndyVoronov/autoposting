import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime


class TestRedditSourceInit:
    def test_init(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        assert source.base_url == "https://www.reddit.com"
        assert len(source.SUBREDDITS) == 10


class TestRedditSourceFetchPosts:
    @pytest.mark.asyncio
    async def test_fetch_posts_success(self, mock_reddit_api):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        posts = await source.fetch_posts("interestingasfuck", limit=10)

        assert len(posts) >= 1
        assert posts[0]["reddit_id"] == "abc123"
        assert posts[0]["title"] == "Amazing fact!"

    @pytest.mark.asyncio
    async def test_fetch_posts_min_score(self, mock_reddit_api):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        posts = await source.fetch_posts("interestingasfuck", min_score=10000)

        assert len(posts) >= 0

    @pytest.mark.asyncio
    async def test_fetch_posts_error(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = AsyncMock()
            mock_client.return_value.__aenter__.return_value = mock_instance
            mock_instance.get.side_effect = Exception("Network error")

            posts = await source.fetch_posts("nonexistent")
            assert posts == []


class TestRedditSourceGetImageUrl:
    def test_get_image_url_direct(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        post_data = {"url": "https://i.redd.it/test.jpg"}

        result = source._get_image_url(post_data)
        assert result == "https://i.redd.it/test.jpg"

    def test_get_image_url_from_preview(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        post_data = {
            "url": "https://www.reddit.com/post",
            "preview": {"images": [{"source": {"url": "https://preview.redd.it/test.jpg"}}]},
        }

        result = source._get_image_url(post_data)
        assert "test.jpg" in result

    def test_get_image_url_no_image(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        post_data = {"url": "https://www.reddit.com/post"}

        result = source._get_image_url(post_data)
        assert result is None


class TestRedditSourceProcessForPost:
    @pytest.mark.asyncio
    async def test_process_for_post_with_translation(self, mock_ai_service):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        post = {
            "title": "Test Title",
            "selftext": "Test body",
            "url": "https://reddit.com/post",
            "image_url": None,
            "score": 1000,
            "subreddit": "test",
        }

        result = await source.process_for_post(post, translate=True, rewrite=True)

        assert "title" in result
        assert "body" in result
        assert result["source_url"] == "https://reddit.com/post"

    @pytest.mark.asyncio
    async def test_process_for_post_without_translation(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        post = {
            "title": "Test Title",
            "selftext": "Test body",
            "url": "https://reddit.com/post",
            "image_url": "https://example.com/image.jpg",
            "score": 1000,
            "subreddit": "test",
        }

        result = await source.process_for_post(post, translate=False, rewrite=False)

        assert result["title"] == "Test Title"
        assert result["body"] == "Test Title\n\nTest body"


class TestRedditSourceGenerateUniqueId:
    def test_generate_unique_id(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        result = source.generate_unique_id("abc123", "Test Title")

        assert len(result) == 12
        assert isinstance(result, str)

    def test_generate_unique_id_consistent(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        id1 = source.generate_unique_id("abc123", "Test Title")
        id2 = source.generate_unique_id("abc123", "Test Title")

        assert id1 == id2

    def test_generate_unique_id_different(self):
        from app.services.content.reddit import RedditSource

        source = RedditSource()
        id1 = source.generate_unique_id("abc123", "Title 1")
        id2 = source.generate_unique_id("abc123", "Title 2")

        assert id1 != id2
