import feedparser
import httpx
from typing import Optional
from datetime import datetime
import hashlib

from app.services.ai import ai_service


class RedditSource:
    SUBREDDITS = [
        "interestingasfuck",
        "todayilearned",
        "mildlyinteresting",
        "Damnthatsinteresting",
        "BeAmazed",
        "educationalgifs",
        "explainlikeimfive",
        "AskReddit",
        "tifu",
        "Showerthoughts",
    ]

    def __init__(self):
        self.base_url = "https://www.reddit.com"

    async def fetch_posts(
        self,
        subreddit: str,
        limit: int = 25,
        min_score: int = 1000,
    ) -> list[dict]:
        url = f"{self.base_url}/r/{subreddit}/hot.json?limit={limit}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "AutopostingBot/1.0"},
                )
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            print(f"Reddit fetch error: {e}")
            return []

        posts = []
        for child in data.get("data", {}).get("children", []):
            post_data = child.get("data", {})

            if post_data.get("score", 0) < min_score:
                continue

            if post_data.get("over_18", False):
                continue

            posts.append(
                {
                    "reddit_id": post_data.get("id"),
                    "title": post_data.get("title"),
                    "selftext": post_data.get("selftext", ""),
                    "url": f"{self.base_url}{post_data.get('permalink', '')}",
                    "image_url": self._get_image_url(post_data),
                    "score": post_data.get("score", 0),
                    "num_comments": post_data.get("num_comments", 0),
                    "subreddit": post_data.get("subreddit"),
                    "author": post_data.get("author"),
                    "created_utc": datetime.fromtimestamp(post_data.get("created_utc", 0)),
                    "is_video": post_data.get("is_video", False),
                }
            )

        return posts

    def _get_image_url(self, post_data: dict) -> Optional[str]:
        url = post_data.get("url", "")

        if not url:
            return None

        image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        if any(url.lower().endswith(ext) for ext in image_extensions):
            return url

        preview = post_data.get("preview", {}).get("images", [])
        if preview:
            return preview[0].get("source", {}).get("url", "").replace("&amp;", "&")

        return None

    async def fetch_rss(self, subreddit: str) -> list[dict]:
        url = f"{self.base_url}/r/{subreddit}/hot.rss"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": "AutopostingBot/1.0"},
                )
                response.raise_for_status()
        except Exception as e:
            print(f"Reddit RSS fetch error: {e}")
            return []

        feed = feedparser.parse(response.text)
        posts = []

        for entry in feed.entries[:25]:
            posts.append(
                {
                    "reddit_id": entry.get("id", "").split("/")[-1] if entry.get("id") else None,
                    "title": entry.get("title"),
                    "selftext": entry.get("summary", ""),
                    "url": entry.get("link"),
                    "image_url": self._extract_image_from_content(
                        entry.get("content", [{}])[0].get("value", "")
                    ),
                    "subreddit": subreddit,
                    "author": entry.get("author"),
                }
            )

        return posts

    def _extract_image_from_content(self, content: str) -> Optional[str]:
        import re

        match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
        if match:
            return match.group(1).replace("&amp;", "&")
        return None

    def generate_unique_id(self, reddit_id: str, title: str) -> str:
        hash_input = f"{reddit_id}:{title}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]

    async def process_for_post(
        self,
        post: dict,
        translate: bool = True,
        rewrite: bool = True,
    ) -> dict:
        title = post.get("title", "")
        body = post.get("selftext", "")

        content = f"{title}"
        if body and len(body) < 1000:
            content += f"\n\n{body}"

        if translate:
            translated = await ai_service.translate_to_russian(content)
            if translated:
                content = translated

        if rewrite:
            rewritten = await ai_service.rewrite_text(content, "увлекательный")
            if rewritten:
                content = rewritten

        return {
            "title": title if not translate else await self._translate_title(title),
            "body": content,
            "source_url": post.get("url"),
            "source_title": post.get("title"),
            "media_urls": [post["image_url"]] if post.get("image_url") else [],
            "ai_metadata": {
                "translated": translate,
                "rewritten": rewrite,
                "original_subreddit": post.get("subreddit"),
                "reddit_score": post.get("score"),
            },
        }

    async def _translate_title(self, title: str) -> str:
        translated = await ai_service.translate_to_russian(title)
        return translated if translated else title


reddit_source = RedditSource()
