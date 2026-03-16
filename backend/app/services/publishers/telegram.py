import httpx
from typing import Optional
from datetime import datetime

from app.config import settings


class TelegramPublisher:
    def __init__(self, token: Optional[str] = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    async def send_message(
        self,
        chat_id: str,
        text: str,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = False,
    ) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={
                        "chat_id": chat_id,
                        "text": text,
                        "parse_mode": parse_mode,
                        "disable_web_page_preview": disable_web_page_preview,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    async def send_photo(
        self,
        chat_id: str,
        photo_url: str,
        caption: Optional[str] = None,
        parse_mode: str = "Markdown",
    ) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                data = {
                    "chat_id": chat_id,
                    "photo": photo_url,
                }
                if caption:
                    data["caption"] = caption[:1024]  # Telegram limit
                    data["parse_mode"] = parse_mode

                response = await client.post(
                    f"{self.base_url}/sendPhoto",
                    json=data,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    async def send_video(
        self,
        chat_id: str,
        video_url: str,
        caption: Optional[str] = None,
        parse_mode: str = "Markdown",
    ) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                data = {
                    "chat_id": chat_id,
                    "video": video_url,
                }
                if caption:
                    data["caption"] = caption[:1024]
                    data["parse_mode"] = parse_mode

                response = await client.post(
                    f"{self.base_url}/sendVideo",
                    json=data,
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    async def edit_message(
        self,
        chat_id: str,
        message_id: int,
        text: str,
        parse_mode: str = "Markdown",
    ) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/editMessageText",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                        "text": text,
                        "parse_mode": parse_mode,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    async def delete_message(
        self,
        chat_id: str,
        message_id: int,
    ) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/deleteMessage",
                    json={
                        "chat_id": chat_id,
                        "message_id": message_id,
                    },
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    async def get_chat(self, chat_id: str) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/getChat",
                    json={"chat_id": chat_id},
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    async def get_me(self) -> dict:
        if not self.token:
            return {"ok": False, "error": "No bot token configured"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{self.base_url}/getMe")
                response.raise_for_status()
                return response.json()
            except Exception as e:
                return {"ok": False, "error": str(e)}

    def format_post(self, title: Optional[str], body: str, source_url: Optional[str] = None) -> str:
        parts = []

        if title:
            parts.append(f"*{self._escape_markdown(title)}*")
            parts.append("")

        parts.append(self._escape_markdown(body))

        if source_url:
            parts.append("")
            parts.append(f"[Источник]({source_url})")

        return "\n".join(parts)

    def _escape_markdown(self, text: str) -> str:
        escape_chars = [
            "_",
            "*",
            "[",
            "]",
            "(",
            ")",
            "~",
            "`",
            ">",
            "#",
            "+",
            "-",
            "=",
            "|",
            "{",
            "}",
            ".",
            "!",
        ]
        for char in escape_chars:
            text = text.replace(char, f"\\{char}")
        return text


telegram_publisher = TelegramPublisher()
