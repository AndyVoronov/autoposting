import httpx
from typing import Optional
from datetime import datetime

from app.config import settings


class VKPublisher:
    def __init__(self, access_token: Optional[str] = None, group_id: Optional[int] = None):
        self.access_token = access_token or settings.VK_ACCESS_TOKEN
        self.group_id = group_id or settings.VK_GROUP_ID
        self.base_url = "https://api.vk.com/method"
        self.api_version = "5.131"

    async def wall_post(
        self,
        message: str,
        attachments: Optional[list[str]] = None,
        publish_date: Optional[int] = None,
    ) -> dict:
        if not self.access_token or not self.group_id:
            return {"error": "VK credentials not configured"}

        params = {
            "access_token": self.access_token,
            "owner_id": f"-{self.group_id}",
            "message": message,
            "v": self.api_version,
        }

        if attachments:
            params["attachments"] = ",".join(attachments)

        if publish_date:
            params["publish_date"] = publish_date

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/wall.post",
                    data=params,
                )
                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    return {"error": data["error"]}

                return {"success": True, "post_id": data.get("response", {}).get("post_id")}
            except Exception as e:
                return {"error": str(e)}

    async def get_upload_server(self, photo_type: str = "wall") -> dict:
        if not self.access_token or not self.group_id:
            return {"error": "VK credentials not configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/photos.getWallUploadServer",
                    params={
                        "access_token": self.access_token,
                        "group_id": self.group_id,
                        "v": self.api_version,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def save_wall_photo(self, photo: str, server: int, hash_value: str) -> dict:
        if not self.access_token or not self.group_id:
            return {"error": "VK credentials not configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/photos.saveWallPhoto",
                    params={
                        "access_token": self.access_token,
                        "group_id": self.group_id,
                        "photo": photo,
                        "server": server,
                        "hash": hash_value,
                        "v": self.api_version,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    async def get_group_info(self) -> dict:
        if not self.access_token or not self.group_id:
            return {"error": "VK credentials not configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{self.base_url}/groups.getById",
                    params={
                        "access_token": self.access_token,
                        "group_id": self.group_id,
                        "v": self.api_version,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"error": str(e)}

    def format_post(self, title: Optional[str], body: str, source_url: Optional[str] = None) -> str:
        parts = []

        if title:
            parts.append(title)
            parts.append("")

        parts.append(body)

        if source_url:
            parts.append("")
            parts.append(f"Подробнее: {source_url}")

        return "\n".join(parts)


vk_publisher = VKPublisher()
