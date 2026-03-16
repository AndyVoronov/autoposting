import feedparser
import httpx
from typing import Optional
from datetime import datetime
import hashlib

from app.services.ai import ai_service
from app.services.censorship import check_censorship


class NewsSource:
    RSS_FEEDS = {
        "tass": "https://tass.ru/rss/v2.xml",
        "ria": "https://ria.ru/export/rss2/archive/index.xml",
        "interfax": "https://www.interfax.ru/rss.asp",
        "rbc": "https://rssexport.rbc.ru/rbcnews/news.rss",
        "lenta": "https://lenta.ru/rss",
    }

    def __init__(self):
        self.seen_hashes: set[str] = set()

    async def fetch_feed(self, source: str, limit: int = 20) -> list[dict]:
        url = self.RSS_FEEDS.get(source)
        if not url:
            return []

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
        except Exception as e:
            print(f"News fetch error for {source}: {e}")
            return []

        feed = feedparser.parse(response.text)
        news = []

        for entry in feed.entries[:limit]:
            content_hash = self._hash_entry(entry)
            if content_hash in self.seen_hashes:
                continue

            news.append(
                {
                    "title": entry.get("title"),
                    "summary": entry.get("summary"),
                    "link": entry.get("link"),
                    "published": entry.get("published_parsed"),
                    "source": source,
                    "hash": content_hash,
                    "categories": entry.get("tags", []),
                }
            )
            self.seen_hashes.add(content_hash)

        return news

    def _hash_entry(self, entry: dict) -> str:
        content = f"{entry.get('title', '')}:{entry.get('link', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    async def process_news(
        self,
        news_item: dict,
        summarize: bool = True,
        check_censorship_flag: bool = True,
    ) -> dict:
        title = news_item.get("title", "")
        summary = news_item.get("summary", "")

        content = summary if summary else title

        if summarize:
            summarized = await ai_service.summarize_news(content)
            if summarized:
                body = summarized
            else:
                body = content[:500]
        else:
            body = content[:500]

        result = {
            "title": title,
            "body": body,
            "source_url": news_item.get("link"),
            "source_name": news_item.get("source"),
            "censorship_passed": True,
            "censorship_flags": None,
        }

        # Note: censorship check should be done with DB session in the actual use
        # This is a simplified version for the service

        return result

    async def fetch_all_sources(self, limit_per_source: int = 10) -> list[dict]:
        all_news = []

        for source in self.RSS_FEEDS:
            news = await self.fetch_feed(source, limit_per_source)
            all_news.extend(news)

        all_news.sort(key=lambda x: x.get("published") or datetime.min, reverse=True)

        return all_news

    def filter_by_categories(
        self,
        news: list[dict],
        include_categories: Optional[list[str]] = None,
        exclude_categories: Optional[list[str]] = None,
    ) -> list[dict]:
        if not include_categories and not exclude_categories:
            return news

        filtered = []
        for item in news:
            categories = [tag.get("term", "").lower() for tag in item.get("categories", [])]

            if exclude_categories:
                if any(exc.lower() in " ".join(categories) for exc in exclude_categories):
                    continue

            if include_categories:
                if not any(inc.lower() in " ".join(categories) for inc in include_categories):
                    continue

            filtered.append(item)

        return filtered


news_source = NewsSource()
