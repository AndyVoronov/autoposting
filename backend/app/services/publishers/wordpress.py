import httpx
from typing import Optional
from datetime import datetime

from app.config import settings


class WordPressPublisher:
    def __init__(
        self,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.url = (url or settings.WP_URL or "").rstrip("/")
        self.username = username or settings.WP_USERNAME
        self.password = password or settings.WP_PASSWORD
        self.api_url = f"{self.url}/wp-json/wp/v2"

    @property
    def auth(self) -> Optional[tuple]:
        if self.username and self.password:
            return (self.username, self.password)
        return None

    async def create_post(
        self,
        title: str,
        content: str,
        status: str = "publish",
        categories: Optional[list[int]] = None,
        tags: Optional[list[int]] = None,
        featured_media: Optional[int] = None,
        slug: Optional[str] = None,
        excerpt: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> dict:
        if not self.auth:
            return {"error": "WordPress credentials not configured"}

        data = {
            "title": title,
            "content": content,
            "status": status,
        }

        if categories:
            data["categories"] = categories
        if tags:
            data["tags"] = tags
        if featured_media:
            data["featured_media"] = featured_media
        if slug:
            data["slug"] = slug
        if excerpt:
            data["excerpt"] = excerpt
        if meta:
            data["meta"] = meta

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/posts",
                    auth=self.auth,
                    json=data,
                )
                response.raise_for_status()
                result = response.json()
                return {"success": True, "post_id": result.get("id"), "url": result.get("link")}
            except httpx.HTTPStatusError as e:
                return {
                    "error": f"HTTP error: {e.response.status_code}",
                    "details": e.response.text,
                }
            except Exception as e:
                return {"error": str(e)}

    async def get_categories(self) -> list[dict]:
        if not self.auth:
            return []

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.api_url}/categories",
                    auth=self.auth,
                    params={"per_page": 100},
                )
                response.raise_for_status()
                return response.json()
            except Exception:
                return []

    async def get_or_create_category(self, name: str, slug: Optional[str] = None) -> Optional[int]:
        categories = await self.get_categories()

        for cat in categories:
            if cat.get("name", "").lower() == name.lower():
                return cat.get("id")
            if slug and cat.get("slug") == slug:
                return cat.get("id")

        if not self.auth:
            return None

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/categories",
                    auth=self.auth,
                    json={"name": name, "slug": slug or name.lower().replace(" ", "-")},
                )
                response.raise_for_status()
                result = response.json()
                return result.get("id")
            except Exception:
                return None

    async def upload_media(
        self,
        file_url: str,
        title: Optional[str] = None,
        alt_text: Optional[str] = None,
    ) -> dict:
        if not self.auth:
            return {"error": "WordPress credentials not configured"}

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                file_response = await client.get(file_url)
                file_response.raise_for_status()

                filename = file_url.split("/")[-1].split("?")[0] or "image.jpg"

                response = await client.post(
                    f"{self.api_url}/media",
                    auth=self.auth,
                    headers={"Content-Disposition": f'attachment; filename="{filename}"'},
                    content=file_response.content,
                )
                response.raise_for_status()
                result = response.json()

                return {
                    "success": True,
                    "media_id": result.get("id"),
                    "url": result.get("source_url"),
                }
            except Exception as e:
                return {"error": str(e)}

    async def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        if not self.auth:
            return {"error": "WordPress credentials not configured"}

        data = {}
        if title:
            data["title"] = title
        if content:
            data["content"] = content
        if status:
            data["status"] = status

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.api_url}/posts/{post_id}",
                    auth=self.auth,
                    json=data,
                )
                response.raise_for_status()
                return {"success": True}
            except Exception as e:
                return {"error": str(e)}

    async def delete_post(self, post_id: int) -> dict:
        if not self.auth:
            return {"error": "WordPress credentials not configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.delete(
                    f"{self.api_url}/posts/{post_id}",
                    auth=self.auth,
                )
                response.raise_for_status()
                return {"success": True}
            except Exception as e:
                return {"error": str(e)}

    def format_content(self, title: str, body: str, source_url: Optional[str] = None) -> str:
        content = f"<h2>{title}</h2>\n\n{body}"

        if source_url:
            content += (
                f'\n\n<p><a href="{source_url}" target="_blank" rel="noopener">Источник</a></p>'
            )

        return content


wordpress_publisher = WordPressPublisher()
